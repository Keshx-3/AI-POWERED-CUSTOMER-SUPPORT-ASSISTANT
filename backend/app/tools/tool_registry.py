import logging
from typing import Any

logger = logging.getLogger(__name__)


def tracking_tool(order_id: str = "ORD-98765") -> dict:
    logger.info("tracking_tool called with order_id=%s", order_id)
    return {
        "order_id": order_id,
        "status": "In Transit",
        "estimated_delivery": "2026-05-20",
        "current_location": "Mumbai Sorting Center",
        "carrier": "ShipRocket",
    }


def refund_tool(order_id: str = "ORD-98765") -> dict:
    logger.info("refund_tool called with order_id=%s", order_id)
    return {
        "order_id": order_id,
        "refund_amount": 2499.0,
        "status": "Approved",
        "estimated_days": 5,
        "payment_method": "Credit Card (xxxx-1234)",
    }


def complaint_tool(category: str = "general", description: str = "") -> dict:
    logger.info("complaint_tool called: category=%s", category)
    return {
        "ticket_id": "TKT-" + str(hash(description))[-6:],
        "category": category,
        "status": "Filed",
        "response_time": "24 hours",
        "message": "Your complaint has been registered. Our team will contact you within 24 hours.",
    }


def escalation_tool(reason: str = "") -> dict:
    logger.info("escalation_tool called: reason=%s", reason)
    return {
        "escalated_to": "Senior Support Manager",
        "ticket_id": "ESC-" + str(hash(reason))[-6:],
        "priority": "High",
        "expected_response": "2 hours",
        "message": "Your case has been escalated to a Senior Support Manager.",
    }


def hotel_tool(city: str = "", max_price: float = 99999) -> dict:
    try:
        limit = float(max_price) if float(max_price) > 0 else 99999
    except (TypeError, ValueError):
        limit = 99999
    logger.info("hotel_tool called: city=%s, max_price=%s, limit=%s", city, max_price, limit)
    hotels = [
        {"name": "Grand Palace Hotel", "price_per_night": 15000, "rating": 4.8, "location": "Dubai Marina", "image_url": ""},
        {"name": "Desert Rose Resort", "price_per_night": 8500, "rating": 4.5, "location": "Palm Jumeirah", "image_url": ""},
        {"name": "City Inn Express", "price_per_night": 3500, "rating": 3.9, "location": "Bur Dubai", "image_url": ""},
        {"name": "Skyline Suites", "price_per_night": 12000, "rating": 4.6, "location": "Downtown Dubai", "image_url": ""},
        {"name": "Budget Stay Hostel", "price_per_night": 1200, "rating": 3.5, "location": "Deira", "image_url": ""},
    ]
    filtered = [h for h in hotels if h["price_per_night"] <= limit]
    return {"city": city or "Dubai", "hotels": filtered, "total": len(filtered)}


def _format_city(city: str, code: str) -> str:
    return f"{city} ({code})" if city and "(" not in city else city or f"Unknown ({code})"


def flight_tool(source: str = "", destination: str = "", date: str = "", max_price: float = 99999) -> dict:
    try:
        limit = float(max_price) if float(max_price) > 0 else 99999
    except (TypeError, ValueError):
        limit = 99999
    logger.info("flight_tool called: %s -> %s on %s, max_price=%s, limit=%s", source, destination, date, max_price, limit)
    flights = [
        {"airline": "IndiGo", "flight_number": "6E-201", "departure": "06:30", "arrival": "09:15", "price": 5500, "duration": "2h 45m"},
        {"airline": "SpiceJet", "flight_number": "SG-104", "departure": "14:00", "arrival": "16:40", "price": 4200, "duration": "2h 40m"},
        {"airline": "Air India", "flight_number": "AI-672", "departure": "08:00", "arrival": "11:30", "price": 7800, "duration": "3h 30m"},
        {"airline": "Vistara", "flight_number": "UK-895", "departure": "16:45", "arrival": "19:20", "price": 6500, "duration": "2h 35m"},
        {"airline": "GoFirst", "flight_number": "G8-321", "departure": "21:00", "arrival": "23:15", "price": 3800, "duration": "2h 15m"},
    ]
    filtered = [f for f in flights if f["price"] <= limit]
    return {
        "source": _format_city(source, "BOM"),
        "destination": _format_city(destination, "DEL"),
        "date": date or "2026-05-15",
        "flights": filtered,
        "total": len(filtered),
    }


TOOL_MAP = {
    "hotel_search": {"func": hotel_tool, "params": ["city", "max_price"]},
    "flight_search": {"func": flight_tool, "params": ["source", "destination", "date", "max_price"]},
    "order_tracking": {"func": tracking_tool, "params": ["order_id"]},
    "refund_request": {"func": refund_tool, "params": ["order_id"]},
    "complaint": {"func": complaint_tool, "params": ["category", "description"]},
    "escalation": {"func": escalation_tool, "params": ["reason"]},
}


def execute_tool(intent: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    tool_def = TOOL_MAP.get(intent)
    if not tool_def:
        logger.warning("Unknown intent: %s", intent)
        return {
            "intent": intent,
            "tool": "unknown",
            "result": {"error": f"No tool found for intent: {intent}"},
            "summary": "I'm not sure how to handle that.",
        }
    params = params or {}
    tool_fn = tool_def["func"]
    valid_params = {k: v for k, v in params.items() if k in tool_def["params"]}
    try:
        result = tool_fn(**valid_params)
        return {"intent": intent, "tool": tool_fn.__name__, "result": result, "summary": _generate_summary(intent, result)}
    except Exception as e:
        logger.error("Tool %s execution failed: %s", intent, e)
        return {"intent": intent, "tool": tool_fn.__name__, "result": {"error": str(e)}, "summary": "Sorry, something went wrong."}


def _generate_summary(intent: str, result: dict) -> str:
    summaries = {
        "hotel_search": lambda r: f"Found {r['total']} hotel(s) in {r['city']}.",
        "flight_search": lambda r: f"Found {r['total']} flight(s) from {r['source']} to {r['destination']}.",
        "order_tracking": lambda r: f"Order {r['order_id']} is {r['status']}. Expected delivery: {r['estimated_delivery']}.",
        "refund_request": lambda r: f"Refund of \u20b9{r['refund_amount']} approved for order {r['order_id']}.",
        "complaint": lambda r: r["message"],
        "escalation": lambda r: r["message"],
    }
    fn = summaries.get(intent)
    return fn(result) if fn else "Task completed."
