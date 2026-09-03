# Toy backing "data" so the labs are self-contained
_ORDERS = {
    "4471": {"status": "Shipped", "eta": "2026-09-05"},
    "4472": {"status": "Processing", "eta": "2026-09-10"},
}
_KB = {
    "refund policy": "Refunds are issued within 5 business days for unused items returned within 30 days.",
    "shipping": "Standard shipping takes 3-5 business days; express takes 1-2.",
}


def search_kb(query: str) -> str:
    for key, content in _KB.items():
        if key in query.lower():
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

# Dispatch table agent/core.py uses to actually invoke the tool the model picked
TOOL_FUNCTIONS = {
    "search_kb": search_kb,
    "get_order_status": get_order_status,
}
