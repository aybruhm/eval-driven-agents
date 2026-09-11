from collections.abc import Callable
from typing import Any

# Toy backing "data" so the labs are self-contained
_ORDERS = {
    "4471": {"status": "Shipped", "eta": "2026-09-05"},
    "4472": {"status": "Processing", "eta": "2026-09-10"},
}
_REFUND_POLICY = "Refunds are issued within 5 business days for unused items returned within 30 days."
_KB = {
    "refund policy": _REFUND_POLICY,
    "return window": _REFUND_POLICY,
    "returns": _REFUND_POLICY,
    "shipping": "Standard shipping takes 3-5 business days; express takes 1-2.",
}


def search_kb(query: str) -> str:
    query = query.lower()
    for key, content in _KB.items():
        if key in query:
            return content

    query_tokens = set(query.split())
    for key, content in _KB.items():
        if query_tokens & set(key.split()):
            return content
    return "No matching knowledge base article found."


def get_order_status(order_id: str) -> dict:
    return _ORDERS.get(order_id, {"error": f"No order found with id {order_id}"})


# JSON schema Claude uses to decide when/how to call each tool
TOOLS = [
    {
        "name": "search_kb",
        "description": "Search the internal knowledge base for policy and general info questions.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The search query"}
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_order_status",
        "description": "Look up the status and ETA of a specific order by its ID.",
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "The order ID, e.g. '4471'",
                }
            },
            "required": ["order_id"],
        },
    },
]

TOOL_FUNCTIONS: dict[str, Callable[..., Any]] = {

    "search_kb": search_kb,
    "get_order_status": get_order_status,
}
