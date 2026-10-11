from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END

# 1) Shared state
class SupportState(TypedDict):
    issue: str
    next: str
    result: str

# 2) supervisor, which is going to decide where to route
def supervisor(state: SupportState):
    issue = state["issue"].lower()

    print("\nSupervisor: Reviewing issue...")

    if "wifi" in issue or "internet" in issue:
        destination = "network_support"
    else:
        destination = "hardware_support"
    
    print("Supervisor: routing to ", destination)

    return {"next": destination}

# 3) network specialist
def network_support(state: SupportState):
    print("Network specialist: checking the wi-fi status")

    return {
        "result": "network support investigated the wifi issue."
    }

# 4) hardware specialist
def hardware_support(state: SupportState):
    print("Hardware specialist: checking the laptop issue")

    return {
        "result": "Hardware support investigated the laptop issue."
    }


# 6) Build graph
builder = StateGraph(SupportState)

builder.add_node("supervisor", supervisor)
builder.add_node("network_support", network_support)
builder.add_node("hardware_support", hardware_support)

builder.add_edge(START, "supervisor")


def route(state: SupportState):
    if state["result"]:
        return END
    
    return state["next"]

builder.add_conditional_edges(
    "supervisor",
    lambda state: END if state["result"] else state["next"],
    {
        "network_support": "network_support",
        "hardware_support": "hardware_support",
        END: END
    }
)

builder.add_edge("network_support", "supervisor")
builder.add_edge("hardware_support", "supervisor")


graph = builder.compile()

result = graph.invoke({
    "issue": "My office wifi is not working",
    "next": "",
    "result": ""
})

print("\nFinal result : ", result["result"])