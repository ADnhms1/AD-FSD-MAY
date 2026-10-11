from typing import TypedDict, Annotated, Literal
import operator

from langgraph.graph import StateGraph, START, END

# 1) Shared state
class OrderState(TypedDict):
    ticket: str
    findings: Annotated[list[str], operator.add]
    next: Literal["billing", "shipping", "FINISH"]
    shipping_done: bool
    billing_done: bool

# 2) Supervisor orchestrates the workflow
def supervisor(state: OrderState):
    print("\nSupervisor: Reviewing customer request...")

    if not state["shipping_done"]:
        print("Supervisor: Shipping investigation required")
        return {"next": "shipping"}
    
    if not state["billing_done"]:
        print("Supervisor: Billing investigation required")
        return {"next": "billing"}

    print("Supervisor: All investigations complete. Proceeding to finish.")
    return {"next": "FINISH"}

# 3. Shipping speciality
def shipping(state: OrderState):
    print("Shipping specialist: Checking delivery status...")

    return {
        "findings":[
            "SHIPPING: Order is delayed in transit."
        ],
        "shipping_done": True
    }

# 4. Billing speciality
def billing(state: OrderState):
    print("Billing specialist: checking payment records...")

    return {
        "findings": [
            "BILLING: Duplicate charge reported; "
            "transaction verification is required."
        ],
        "billing_done": True
    }

# 5) Router
def route(state: OrderState):
    if(state["next"] == "FINISH"):
        return END
    
    return state["next"]

# 6) create the builder
builder = StateGraph(OrderState)

builder.add_node("supervisor", supervisor)
builder.add_node("shipping", shipping)
builder.add_node("billing", billing)

builder.add_edge(START, "supervisor")

builder.add_conditional_edges(
    "supervisor",
    route,
    {
        "shipping": "shipping",
        "billing": "billing",
        END: END
    }
)

builder.add_edge("shipping", "supervisor")
builder.add_edge("billing", "supervisor")

graph = builder.compile()


# 7) run this process

if __name__ == "__main__":
    result = graph.invoke({
        "ticket": (
            "My order has not arrived, and i was charged twice."
        ),
        "findings": [],
        "next": "shipping",
        "shipping_done": False,
        "billing_done": False
    })

    print("\n =========== Investigation Summary ============== ")

    for finding in result["findings"]:
        print("-", finding)