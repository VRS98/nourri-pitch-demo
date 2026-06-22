from typing import TypedDict, List, Dict, Any, Annotated
import operator
from datetime import datetime, timezone

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

from agent.tools import get_tools
from agent.llm import get_llm
from agent.trace import log_event
from agent.util import content_text
from guardrails.input_validation import validate_input

class OrderState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    missing_ingredients: List[str]
    cart: List[Dict[str, Any]]
    total_price: float
    status: str # "sourcing", "awaiting_approval", "ordered", "cancelled", "error"
    error_message: str
    order_id: str

def create_agent_graph():
    # Tools: prefer the MCP catalog server, fall back to in-process tools.
    tools = get_tools()

    # Model: real Gemini if GEMINI_API_KEY is set, else a deterministic mock.
    llm = get_llm()
    llm_with_tools = llm.bind_tools(tools)
    
    # Define Nodes
    def validate_node(state: OrderState):
        ingredients = state.get("missing_ingredients", [])
        validation = validate_input(ingredients)
        if not validation["valid"]:
            log_event("guardrail.input_validation", triggered=True,
                      reason=validation["reason"], input=ingredients)
            return {
                "status": "error",
                "error_message": validation["reason"],
                "messages": [AIMessage(content=f"Guardrail triggered: {validation['reason']}")]
            }
        log_event("guardrail.input_validation", triggered=False, items=len(ingredients))
        return {"status": "sourcing"}

    def sourcing_agent(state: OrderState):
        messages = state["messages"]
        # If it's the first time sourcing
        if len(messages) == 0 or (len(messages) == 1 and isinstance(messages[0], AIMessage) and "Guardrail" in messages[0].content):
            sys_msg = HumanMessage(content=f"Find sourcing for these missing ingredients: {', '.join(state['missing_ingredients'])}. Always check local producers first. If local is unavailable, check supermarket fallback. Once you have checked all items, compile the results and call the finalize_cart tool or just state you are done.")
            messages = [sys_msg]
            
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}
        
    # Wrap ToolNode so every tool call and result is written to the audit log.
    base_tool_node = ToolNode(tools)

    def tool_node(state: OrderState):
        last = state["messages"][-1]
        for tc in getattr(last, "tool_calls", None) or []:
            log_event("tool.call", name=tc.get("name"), args=tc.get("args"))
        result = base_tool_node.invoke(state)
        for msg in result.get("messages", []):
            log_event("tool.result", name=getattr(msg, "name", ""),
                      result=content_text(msg.content))
        return result

    def process_cart(state: OrderState):
        # Compile the cart from the sourcing tool results in the message history.
        import json
        cart = []
        total = 0.0
        seen = set()  # dedup by ingredient; local results come first, so local wins

        for msg in state["messages"]:
            tool_name = getattr(msg, "name", "")
            if tool_name not in ("check_local_producer", "check_supermarket_fallback"):
                continue
            try:
                data = json.loads(content_text(msg.content))
            except (ValueError, TypeError):
                continue
            ingredient = data.get("ingredient")
            if data.get("available") and ingredient not in seen:
                seen.add(ingredient)
                cart.append({
                    "ingredient": ingredient,
                    "source": data.get("source"),
                    "price": data.get("price"),
                    "channel": "local" if tool_name == "check_local_producer" else "supermarket",
                })
                total += float(data.get("price", 0))

        total = round(total, 2)
        log_event("cart.compiled", items=len(cart), total_price=total,
                  cart=cart, status="awaiting_approval")
        return {"cart": cart, "total_price": total, "status": "awaiting_approval"}
        
    def order_execution(state: OrderState):
        if state["status"] == "cancelled":
            log_event("order.cancelled", total_price=state.get("total_price", 0.0),
                      items=len(state.get("cart", [])))
            return {"messages": [AIMessage(content="Order was cancelled by the user.")]}
        order_id = f"NR-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
        log_event("order.placed", order_id=order_id, total_price=state["total_price"],
                  items=len(state.get("cart", [])))
        return {
            "status": "ordered",
            "order_id": order_id,
            "messages": [AIMessage(content=f"Order placed successfully for €{state['total_price']}. Ref {order_id}")]
        }

    # Build Graph
    workflow = StateGraph(OrderState)
    
    workflow.add_node("validate", validate_node)
    workflow.add_node("agent", sourcing_agent)
    workflow.add_node("tools", tool_node)
    workflow.add_node("process_cart", process_cart)
    workflow.add_node("execute", order_execution)
    
    # Edges
    workflow.add_edge(START, "validate")
    
    def route_validation(state: OrderState):
        if state.get("status") == "error":
            return END
        return "agent"
        
    workflow.add_conditional_edges("validate", route_validation)
    
    def route_tools(state: OrderState):
        messages = state["messages"]
        last_message = messages[-1]
        # If LLM makes a tool call, route to tools
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        # Otherwise, process the cart
        return "process_cart"
        
    workflow.add_conditional_edges("agent", route_tools)
    workflow.add_edge("tools", "agent")
    
    # HITL interruption happens here
    workflow.add_edge("process_cart", "execute")
    workflow.add_edge("execute", END)
    
    # Compile with MemorySaver to allow interrupts
    memory = MemorySaver()
    graph = workflow.compile(checkpointer=memory, interrupt_before=["execute"])
    
    return graph
