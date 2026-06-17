import re
import os

from commerce_api import escalate_to_human, get_listing_count, get_order


ESCALATION_TERMS = (
    "angry",
    "unacceptable",
    "complaint",
    "refund dispute",
    "chargeback",
    "human",
    "manager",
)


def classify_intent(message: str) -> str:
    normalized = message.lower()

    if any(term in normalized for term in ESCALATION_TERMS):
        return "ESCALATE"

    if re.search(r"\b(order|tracking|shipped|shipment|delivered)\b", normalized):
        return "ORDER_STATUS"

    product_count_terms = ("how many products", "how many listings", "product count", "listing count")
    if any(term in normalized for term in product_count_terms):
        return "PRODUCT_COUNT"

    return "RAG"


def extract_order_id(message: str) -> str:
    match = re.search(r"#?(\d{4,})", message)
    return match.group(1) if match else ""


def answer_message_rule_based(message: str, platform: str = "etsy") -> dict:
    intent = classify_intent(message)

    if intent == "PRODUCT_COUNT":
        result = get_listing_count(platform=platform)
        answer = (
            f"The {platform.title()} shop currently has "
            f"{result['active_listing_count']} active listings "
            f"out of {result['total_listing_count']} total listing records."
        )
        return {"intent": intent, "answer": answer, "tool_result": result, "sources": []}

    if intent == "ORDER_STATUS":
        order_id = extract_order_id(message)
        if not order_id:
            return {
                "intent": intent,
                "answer": "Please provide your order number so I can check the order status.",
                "tool_result": None,
                "sources": [],
            }

        result = get_order(order_id=order_id, platform=platform)
        if result is None:
            return {
                "intent": intent,
                "answer": f"I could not find order #{order_id}. Please check the order number.",
                "tool_result": None,
                "sources": [],
            }

        answer = (
            f"Order #{order_id} is {result['status']}. Carrier: {result['carrier']}. "
            f"Tracking: {result['tracking_number']}. Estimated delivery: "
            f"{result['estimated_delivery']}."
        )
        return {"intent": intent, "answer": answer, "tool_result": result, "sources": []}

    if intent == "ESCALATE":
        result = escalate_to_human(reason="customer_support_review", platform=platform)
        return {
            "intent": intent,
            "answer": (
                "I am sorry this has been frustrating. I will escalate this to a human support "
                "teammate so they can review the issue and respond with the right next step."
            ),
            "tool_result": result,
            "sources": [],
        }

    from rag_service import answer_with_rag

    rag_result = answer_with_rag(message)
    return {
        "intent": intent,
        "answer": rag_result["answer"],
        "tool_result": None,
        "sources": rag_result["sources"],
    }


def should_use_openai_tool_router() -> bool:
    router_mode = os.getenv("AGENT_ROUTER", "openai").lower()
    return router_mode == "openai" and bool(os.getenv("OPENAI_API_KEY"))


def answer_message(message: str, platform: str = "etsy") -> dict:
    if should_use_openai_tool_router():
        from openai_tool_router import answer_message_with_tools

        return answer_message_with_tools(message=message, platform=platform)

    return answer_message_rule_based(message=message, platform=platform)
