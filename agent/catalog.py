"""Shared ingredient catalog + pure lookup logic.

Both the in-process LangChain tools (agent/tools.py) and the FastMCP server
(mcp_server/catalog_server.py) import from here, so the local-producer and
supermarket data live in exactly one place.
"""
import random

# Mock database for local producers
LOCAL_PRODUCERS = {
    "oat milk": {"available": True, "price": 3.80, "source": "Radicle Urban Farms"},
    "spinach": {"available": True, "price": 2.50, "source": "Green Valley Cooperative"},
    "eggs": {"available": True, "price": 4.20, "source": "Sunrise Dairy Co-op"},
    "mushrooms": {"available": True, "price": 5.00, "source": "Forest Edge Mushroom Lab"},
    "harissa paste": {"available": False},  # Not locally available
}

# Mock database for supermarket fallback
SUPERMARKET = {
    "oat milk": {"available": True, "price": 2.90, "source": "Monoprix"},
    "spinach": {"available": True, "price": 1.90, "source": "Carrefour"},
    "eggs": {"available": True, "price": 3.50, "source": "Monoprix"},
    "mushrooms": {"available": True, "price": 4.00, "source": "Carrefour"},
    "harissa paste": {"available": True, "price": 2.10, "source": "Carrefour"},
    "parmesan cheese": {"available": True, "price": 4.50, "source": "Monoprix"},
    "olive oil": {"available": True, "price": 7.50, "source": "Carrefour"},
}


def _match(catalog: dict, ingredient: str):
    """Simple fuzzy match: case-insensitive substring either direction."""
    key = ingredient.lower().strip()
    for name, data in catalog.items():
        if name in key or key in name:
            return data
    return None


def lookup_local(ingredient: str) -> dict:
    """Pure lookup against the local-producer catalog."""
    data = _match(LOCAL_PRODUCERS, ingredient)
    if data and data.get("available"):
        return {"ingredient": ingredient, "available": True,
                "price": data["price"], "source": data["source"]}
    return {"ingredient": ingredient, "available": False,
            "reason": "Not available from local producers."}


def lookup_supermarket(ingredient: str) -> dict:
    """Pure lookup against the supermarket-fallback catalog.

    Unknown items get a deterministic estimated price (seeded by name) so the
    mock stays reproducible across runs instead of using live randomness.
    """
    data = _match(SUPERMARKET, ingredient)
    if data and data.get("available"):
        return {"ingredient": ingredient, "available": True,
                "price": data["price"], "source": data["source"]}

    # Deterministic estimate for items not in the catalog (seed by name).
    rng = random.Random(ingredient.lower().strip())
    price = round(rng.uniform(1.5, 6.0), 2)
    source = rng.choice(["Carrefour", "Monoprix"])
    return {"ingredient": ingredient, "available": True,
            "price": price, "source": source, "note": "Estimated"}
