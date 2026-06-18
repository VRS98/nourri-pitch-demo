import re

def validate_input(ingredients_list: list) -> dict:
    """
    Guardrail: Validates input to prevent prompt injection or out-of-scope requests.
    Returns {"valid": True} or {"valid": False, "reason": str}
    """
    if not ingredients_list:
        return {"valid": False, "reason": "Empty input provided."}
    
    # Guardrail: Limit number of items to prevent abuse
    if len(ingredients_list) > 10:
        return {"valid": False, "reason": "Maximum of 10 missing ingredients allowed per order."}
    
    # Guardrail: Simple refuse list for prompt injection / non-food items
    refuse_patterns = [
        r"ignore previous", r"system prompt", r"you are a", r"forget", 
        r"bypass", r"execute", r"import os", r"password", r"drop table",
        r"gun", r"weapon", r"poison", r"bomb"
    ]
    
    for item in ingredients_list:
        if not isinstance(item, str):
            return {"valid": False, "reason": "Invalid data type. Must be a list of strings."}
            
        for pattern in refuse_patterns:
            if re.search(pattern, item, re.IGNORECASE):
                return {"valid": False, "reason": f"Input '{item}' violates security policies."}
                
        # Must be somewhat reasonable length for a food item
        if len(item) > 40:
            return {"valid": False, "reason": f"Input '{item}' is too long to be a valid food item."}
            
    return {"valid": True}

def check_hitl_required(total_price: float, max_auto_price: float = 10.0) -> bool:
    """
    Guardrail: Decides if Human-In-The-Loop approval is required.
    For MVP, we always require it before ordering, but programmatically it
    triggers heavily if price > max_auto_price.
    Actually, per the guidelines, "Agent cannot charge without Confirm Order prompt".
    So this will always return True, but we can log the reason.
    """
    return True
