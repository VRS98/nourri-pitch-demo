import random
import time
from langchain_core.tools import tool

# Mock Database for Local Producers and Supermarkets
LOCAL_PRODUCERS = {
    "oat milk": {"available": True, "price": 3.80, "source": "Radicle Urban Farms"},
    "spinach": {"available": True, "price": 2.50, "source": "Green Valley Cooperative"},
    "eggs": {"available": True, "price": 4.20, "source": "Sunrise Dairy Co-op"},
    "mushrooms": {"available": True, "price": 5.00, "source": "Forest Edge Mushroom Lab"},
    "harissa paste": {"available": False}, # Not locally available
}

SUPERMARKET = {
    "oat milk": {"available": True, "price": 2.90, "source": "Monoprix"},
    "spinach": {"available": True, "price": 1.90, "source": "Carrefour"},
    "eggs": {"available": True, "price": 3.50, "source": "Monoprix"},
    "mushrooms": {"available": True, "price": 4.00, "source": "Carrefour"},
    "harissa paste": {"available": True, "price": 2.10, "source": "Carrefour"},
    "parmesan cheese": {"available": True, "price": 4.50, "source": "Monoprix"},
    "olive oil": {"available": True, "price": 7.50, "source": "Carrefour"}
}

@tool
def check_local_producer(ingredient: str) -> dict:
    """
    Checks if an ingredient is available from local producers.
    Args:
        ingredient: The name of the ingredient (e.g., 'oat milk').
    Returns:
        dict: Availability, price, and source.
    """
    # Simulate API latency
    time.sleep(0.5)
    ingredient = ingredient.lower()
    
    # Simple fuzzy match simulation
    for key, data in LOCAL_PRODUCERS.items():
        if key in ingredient or ingredient in key:
            if data["available"]:
                return {"available": True, "price": data["price"], "source": data["source"]}
    
    return {"available": False, "reason": "Not available from local producers."}

@tool
def check_supermarket_fallback(ingredient: str) -> dict:
    """
    Checks if an ingredient is available from fallback supermarkets (Monoprix, Carrefour).
    Call this ONLY if check_local_producer returns available=False.
    Args:
        ingredient: The name of the ingredient.
    Returns:
        dict: Availability, price, and source.
    """
    # Simulate API latency
    time.sleep(0.5)
    ingredient = ingredient.lower()
    
    for key, data in SUPERMARKET.items():
        if key in ingredient or ingredient in key:
            if data["available"]:
                return {"available": True, "price": data["price"], "source": data["source"]}
            
    # If not found at all
    # Fallback to random assignment for demo purposes if not in DB
    price = round(random.uniform(1.5, 6.0), 2)
    source = random.choice(["Carrefour", "Monoprix"])
    return {"available": True, "price": price, "source": source, "note": "Estimated"}
