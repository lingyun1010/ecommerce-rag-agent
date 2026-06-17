from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Listing:
    id: str
    title: str
    status: str
    price_aud: float
    inventory: int


@dataclass(frozen=True)
class Order:
    id: str
    status: str
    carrier: str
    tracking_number: str
    estimated_delivery: str


LISTINGS = [
    Listing("L-1001", "SILK & PEARL Nourishing Body Soap", "active", 34.0, 18),
    Listing("L-1002", "Natural Ox Horn Classic Comb", "active", 94.0, 5),
    Listing("L-1003", "DISCOVERY SET SHAMPOO BAR COLLECTION", "active", 54.0, 12),
    Listing("L-1004", "Herbal Scalp Massage Comb", "active", 54.0, 7),
    Listing("L-1005", "Pure Cotton Hair Drying Wrap", "active", 34.0, 21),
    Listing("L-1006", "Carbonized Wooden Soap Dish", "active", 19.0, 15),
    Listing("L-1007", "Natural Ox Horn Massage Comb", "active", 72.0, 4),
    Listing("L-1008", "MURA Daily Herbal Haircare Kit", "active", 168.0, 6),
    Listing("L-1009", "CYPRESS & USMA Root Strength Shampoo Bar", "active", 34.0, 25),
    Listing("L-1010", "CLOVE BLOSSOM Smoothing Shampoo Bar", "active", 34.0, 19),
    Listing("L-1011", "GINGER & CALENDULA Scalp Vitality Shampoo Bar", "active", 34.0, 22),
    Listing("L-1012", "TEA CAKE & FO-TI Heritage Repair Shampoo Bar", "active", 34.0, 16),
]

ORDERS = {
    "1001": Order("1001", "shipped", "Australia Post", "AU123456789", "2026-06-20"),
    "1002": Order("1002", "processing", "Not assigned yet", "Not available yet", "2026-06-24"),
    "1003": Order("1003", "delivered", "Australia Post", "AU987654321", "2026-06-12"),
}


def get_listing_count(platform: str = "etsy") -> dict:
    active_count = sum(1 for listing in LISTINGS if listing.status == "active")
    return {
        "platform": platform,
        "active_listing_count": active_count,
        "total_listing_count": len(LISTINGS),
    }


def get_order(order_id: str, platform: str = "etsy") -> Optional[dict]:
    order = ORDERS.get(order_id)
    if order is None:
        return None

    return {
        "platform": platform,
        "order_id": order.id,
        "status": order.status,
        "carrier": order.carrier,
        "tracking_number": order.tracking_number,
        "estimated_delivery": order.estimated_delivery,
    }
