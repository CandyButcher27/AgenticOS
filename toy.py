from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command, interrupt


class State(TypedDict):
    idea: str
    architecture: str
    approved: bool
    result: str


def architect(state: State) -> dict:
    arch = f"FastAPI + Postgres + 3 services, for idea: {state['idea']!r}"
    return {"architecture": arch}


def human_checkpoint(state: State) -> dict:
    decision = interrupt(
        {
            "question": "Approve this architecture? (approve / reject)",
            "architecture": state["architecture"],
        }
    )
    return {"approved": decision == "approve"}


def build(state: State) -> dict:
    if not state["approved"]:
        return {"result": "REJECTED by human — pipeline stopped before build."}
    return {"result": f"Built code from approved architecture: {state['architecture']}"}


def make_graph():
    g = StateGraph(State)
    g.add_node("architect", architect)
    g.add_node("human_checkpoint", human_checkpoint)
    g.add_node("build", build)
    g.add_edge(START, "architect")
    g.add_edge("architect", "human_checkpoint")
    g.add_edge("human_checkpoint", "build")
    g.add_edge("build", END)
    return g.compile(checkpointer=InMemorySaver())


if __name__ == "__main__":
    graph = make_graph()
    config = {"configurable": {"thread_id": "demo-1"}}

    paused = graph.invoke({"idea": "a todo app"}, config)
    print("=== RUN 1: graph ran until it hit interrupt() ===")
    print("Interrupt payload sent to human:")
    print(paused["__interrupt__"][0].value)
    print()

    snapshot = graph.get_state(config)
    print("Graph is parked. Next node waiting:", snapshot.next)
    print()

    decision = "approve"
    resumed = graph.invoke(Command(resume=decision), config)
    print(f"=== RUN 2: resumed same thread with decision={decision!r} ===")
    print("Final state result:")
    print(resumed["result"])
