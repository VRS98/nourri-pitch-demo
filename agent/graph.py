import os
from typing import TypedDict, List, Dict, Any, Annotated
import operator

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

from agent.tools import check_local_producer, check_supermarket_fallback
from guardrails.input_validation import validate_input

class OrderState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    missing_ingredients: List[str]
    cart: List[Dict[str, Any]]
    total_price: float
    status: str # "sourcing", "awaiting_approval", "ordered", "cancelled", "error"
    error_message: str

def create_agent_graph():
    # Initialize LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0,
        api_key=os.environ.get("GEMINI_API_KEY", "dummy") # Handled by env
    )
    
    tools = [check_local_producer, check_supermarket_fallback]
    llm_with_tools = llm.bind_tools(tools)
    
    # Define Nodes
    def validate_node(state: OrderState):
        ingredients = state.get("missing_ingredients", [])
        validation = validate_input(ingredients)
        if not validation["valid"]:
            return {
                "status": "error", 
                "error_message": validation["reason"],
                "messages": [AIMessage(content=f"Guardrail triggered: {validation['reason']}")]
            }
        return {"status": "sourcing"}

    def sourcing_agent(state: OrderState):
        messages = state["messages"]
        # If it's the first time sourcing
        if len(messages) == 0 or (len(messages) == 1 and isinstance(messages[0], AIMessage) and "Guardrail" in messages[0].content):
            sys_msg = HumanMessage(content=f"Find sourcing for these missing ingredients: {', '.join(state['missing_ingredients'])}. Always check local producers first. If local is unavailable, check supermarket fallback. Once you have checked all items, compile the results and call the finalize_cart tool or just state you are done.")
            messages = [sys_msg]
            
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}
        
    tool_node = ToolNode(tools)
    
    def process_cart(state: OrderState):
        # In a real system, the LLM would emit a structured output.
        # Here we simulate cart processing based on the tool messages history.
        cart = []
        total = 0.0
        
        # Simple extraction from tool messages for demo purposes
        for msg in state["messages"]:
            if getattr(msg, "name", "") in ["check_local_producer", "check_supermarket_fallback"]:
                try:
                    import json
                    data = json.loads(msg.content)
                    if data.get("available"):
                        # Extract ingredient name from the tool call that generated this
                        # This is a bit hacky for the demo, normally we'd use a structured output LLM node
                        cart.append({
                            "source": data.get("source"),
                            "price": data.get("price")
                        })
                        total += float(data.get("price", 0))
                except Exception:
                    pass
        
        return {
            "cart": cart,
            "total_price": round(total, 2),
            "status": "awaiting_approval"
        }
        
    def order_execution(state: OrderState):
        if state["status"] == "cancelled":
            return {"messages": [AIMessage(content="Order was cancelled by the user.")]}
        return {
            "status": "ordered",
            "messages": [AIMessage(content=f"Order placed successfully for €{state['total_price']}.")]
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
