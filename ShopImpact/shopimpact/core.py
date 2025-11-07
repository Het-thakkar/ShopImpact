"""Minimal core for the ShopImpact demo.
Provides DEFAULT_MULTIPLIERS, helpers to compute CO2 for a purchase, and a small set
of curated alternatives used by the Streamlit UI.
"""
from datetime import datetime

DEFAULT_MULTIPLIERS = {
    "Groceries": 0.05,
    "Electronics": 0.50,
    "Clothing": 0.20,
    "Furniture": 0.40,
    "Toys": 0.15,
    "Books": 0.03,
    "Transport": 0.25,
}


def get_multiplier_for_category(category: str) -> float:
    """Return the multiplier (kg CO2 per USD) for a category.
    Falls back to a conservative default if unknown.
    """
    return float(DEFAULT_MULTIPLIERS.get(category, 0.10))


def record_to_entry(category: str, brand: str, price: float, quantity: int = 1, note: str = "") -> dict:
    """Create a stored entry dict matching what the UI expects.
    Keys: ts, category, brand, price, quantity, multiplier, co2, note
    """
    mult = get_multiplier_for_category(category)
    try:
        price_f = float(price)
    except Exception:
        price_f = 0.0
    try:
        qty_i = int(quantity)
    except Exception:
        qty_i = 1

    co2 = mult * price_f * qty_i
    return {
        "ts": datetime.now().isoformat(),
        "category": category,
        "brand": brand or "",
        "price": float(price_f),
        "quantity": int(qty_i),
        "multiplier": float(mult),
        "co2": float(co2),
        "note": note or "",
    }


# small curated alternatives mapping for demo suggestions
_ALTERNATIVES = {
    "Groceries": [
        {"product": "Local veggies", "brand": "FarmFresh", "mult": 0.04},
        {"product": "Bulk grains", "brand": "GoodGrain", "mult": 0.03},
    ],
    "Electronics": [
        {"product": "Refurb phone", "brand": "ReNew", "mult": 0.30},
        {"product": "Energy-smart TV", "brand": "EcoView", "mult": 0.35},
    ],
    "Clothing": [
        {"product": "Organic cotton tee", "brand": "PureWear", "mult": 0.12},
        {"product": "Second-hand jacket", "brand": "Thrifted", "mult": 0.05},
    ],
}


def suggest_alternatives(category: str):
    """Return a list of alternative products for the given category.
    Each item is a dict with keys: product, brand, mult.
    """
    return _ALTERNATIVES.get(category, [])
