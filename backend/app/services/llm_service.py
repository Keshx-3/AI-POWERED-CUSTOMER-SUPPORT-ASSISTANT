import json
import logging
import re
from typing import Optional
from app.tools.tool_registry import execute_tool

logger = logging.getLogger(__name__)

OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3.2:1b"

INTENT_SYSTEM_PROMPT = """You are an intent classifier for customer support. Classify the user's intent and extract parameters. Return ONLY valid JSON.

Intents:
- "hotel_search": params: city (str), max_price (float)
- "flight_search": params: source (str), destination (str), date (str)
- "order_tracking": params: order_id (str)
- "refund_request": params: order_id (str)
- "complaint": params: category (str), description (str)
- "escalation": params: reason (str)
- "general": greeting/thanks/chitchat. params: {}

Rules:
- Follow-up like "cheaper ones" after hotels → hotel_search with previous city + max_price
- Follow-up like "earlier flights" after flights → flight_search with previous route
- Missing params → use conversation context, else OMIT the param entirely (do NOT set to 0)

Respond: {"intent": "...", "params": {...}, "reply_to_user": "..."}"""

import httpx


async def classify_and_extract(
    user_message: str,
    conversation_context: str,
    model: str = OLLAMA_MODEL,
) -> dict:
    messages = [
        {"role": "system", "content": INTENT_SYSTEM_PROMPT},
        {"role": "user", "content": f"Conversation context:\n{conversation_context}\n\nUser message: {user_message}"},
    ]

    payload = {
        "model": model,
        "messages": messages,
        "format": "json",
        "stream": False,
        "options": {"temperature": 0.1, "num_predict": 512},
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(f"{OLLAMA_BASE_URL}/api/chat", json=payload)
            resp.raise_for_status()
            data = resp.json()
            content = data["message"]["content"].strip()
            logger.info("LLM response: %s", content)
            parsed = json.loads(content)
    except Exception as e:
        logger.error("LLM call failed: %s. Falling back.", e)
        parsed = _fallback_classify(user_message, conversation_context)

    intent = parsed.get("intent", "general")
    params = parsed.get("params", {})
    reply_to_user = _safe_reply(parsed.get("reply_to_user"))

    _infer_price_if_missing(intent, params, user_message)

    if intent != "general":
        tool_result = execute_tool(intent, params)
        return {
            "intent": intent,
            "params": params,
            "reply": reply_to_user + " " + tool_result.get("summary", ""),
            "data": tool_result["result"],
            "ui_type": _intent_to_ui_type(intent),
        }

    return {
        "intent": "general",
        "params": {},
        "reply": reply_to_user,
        "data": None,
        "ui_type": None,
    }


def _intent_to_ui_type(intent: str) -> Optional[str]:
    return {
        "hotel_search": "hotel_list",
        "flight_search": "flight_list",
        "order_tracking": "tracking_info",
        "refund_request": "refund_info",
        "complaint": "complaint_status",
        "escalation": "escalation_status",
    }.get(intent)


def _fallback_classify(message: str, context: str = "") -> dict:
    msg = message.lower()

    # --- Detect follow-ups from conversation context ---
    last_intent = _extract_last_intent(context)

    if last_intent == "hotel_search" and _is_followup(msg):
        return {
            "intent": "hotel_search",
            "params": {"city": _extract_city(context) or _extract_city(message) or "Dubai", "max_price": _extract_price(msg)},
            "reply_to_user": "Here are some more affordable options!",
        }

    if last_intent == "flight_search" and _is_followup(msg):
        src, dst = _extract_route(context)
        return {
            "intent": "flight_search",
            "params": {"source": src or "Mumbai", "destination": dst or "Delhi"},
            "reply_to_user": "Here are more flight options!",
        }

    # --- Direct intent matching ---
    if any(w in msg for w in ["hotel", "stay", "room", "accommodation", "resort"]):
        return {"intent": "hotel_search", "params": {"city": _extract_city(message)}, "reply_to_user": "Here are some hotels for you!"}

    if any(w in msg for w in ["flight", "fly", "plane", "airport", "travel"]):
        src, dst = _extract_route_from_msg(message)
        return {"intent": "flight_search", "params": {"source": src, "destination": dst}, "reply_to_user": f"Here are flights from {src or 'Mumbai'} to {dst or 'Delhi'}!"}

    if any(w in msg for w in ["track", "delivery", "shipping", "where is"]):
        return {"intent": "order_tracking", "params": {}, "reply_to_user": "Let me check your order status."}

    if any(w in msg for w in ["refund", "money back", "return", "reimburs"]):
        return {"intent": "refund_request", "params": {}, "reply_to_user": "I'll help you with the refund process."}

    if any(w in msg for w in ["complaint", "issue", "problem", "not happy", "dissatisfied"]):
        return {"intent": "complaint", "params": {"category": "general"}, "reply_to_user": "I'm sorry about that. Let me file a complaint for you."}

    if any(w in msg for w in ["manager", "supervisor", "escalate", "speak to", "talk to"]):
        return {"intent": "escalation", "params": {"reason": "Customer requested escalation"}, "reply_to_user": "I'm escalating your request to a senior manager."}

    return {"intent": "general", "params": {}, "reply_to_user": "Hello! How can I help you today? You can ask about hotel bookings, flight searches, order tracking, refunds, or complaints."}


# --- Helper functions ---

def _is_followup(msg: str) -> bool:
    keywords = ["cheap", "cheaper", "affordable", "expensive", "more", "another", "other option", "different", "show more", "earlier", "later", "next", "previous"]
    return any(w in msg for w in keywords)


def _extract_last_intent(context: str) -> str:
    for line in reversed(context.split("\n")):
        if "hotel" in line.lower() or "room" in line.lower():
            return "hotel_search"
        if "flight" in line.lower():
            return "flight_search"
        if "track" in line.lower() or "order" in line.lower():
            return "order_tracking"
        if "refund" in line.lower():
            return "refund_request"
        if "complaint" in line.lower() or "ticket" in line.lower():
            return "complaint"
        if "escalat" in line.lower() or "manager" in line.lower():
            return "escalation"
    return ""


def _extract_city(text: str) -> str:
    known = ["dubai", "mumbai", "delhi", "goa", "bangkok", "paris", "london", "new york", "singapore", "bali", "tokyo", "jaipur"]
    for city in known:
        if city in text.lower():
            return city.title()
    return ""


def _extract_price(msg: str) -> float:
    match = re.search(r"(\d+)\s*(k|thousand)?", msg)
    if match:
        val = float(match.group(1))
        suffix = match.group(2)
        if suffix:
            val *= 1000 if suffix == "k" else 1
        return val
    if any(w in msg for w in ["cheap", "cheaper", "affordable", "budget"]):
        return 5000
    if any(w in msg for w in ["expensive", "luxury"]):
        return 50000
    return 99999


def _extract_route(context: str) -> tuple:
    match = re.search(r"(?:from|between)\s+(\w+(?:\s+\w+)?)\s+(?:to|and)\s+(\w+(?:\s+\w+)?)", context, re.IGNORECASE)
    if match:
        return match.group(1), match.group(2)
    return "", ""


def _extract_route_from_msg(msg: str) -> tuple:
    match = re.search(r"(?:from|between)\s+(\w+(?:\s+\w+)?)\s+(?:to|and)\s+(\w+(?:\s+\w+)?)", msg, re.IGNORECASE)
    if match:
        return match.group(1), match.group(2)
    return "", ""


def _safe_reply(val: object) -> str:
    if isinstance(val, str):
        return val
    if isinstance(val, dict):
        return next((v for v in val.values() if isinstance(v, str)), "Let me help you with that.")
    if val is None:
        return "Let me help you with that."
    return str(val)


def _infer_price_if_missing(intent: str, params: dict, user_message: str) -> None:
    if intent != "hotel_search":
        return
    if "max_price" in params and params["max_price"]:
        return
    msg = user_message.lower()
    cheap_words = ["cheap", "cheaper", "cheapest", "affordable", "budget", "low", "inexpensive", "economy", "discount"]
    if any(w in msg for w in cheap_words):
        params["max_price"] = 5000.0
