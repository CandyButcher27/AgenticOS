from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt

from state import AgentOSState
from agents.idea_refiner import idea_refiner
from agents.architect import architect
from agents.code_writer import code_writer
from agents.github_agent import github_agent


def human_checkpoint(state: AgentOSState) -> dict:
    decision = interrupt(
        {
            "question": "Approve this architecture? (approve / reject)",
            "architecture": state["architecture"],
        }
    )
    return {"human_approved": decision == "approve", "current_agent": "human_checkpoint"}


def route_after_checkpoint(state: AgentOSState) -> str:
    return "code_writer" if state["human_approved"] else END


def make_graph():
    g = StateGraph(AgentOSState)
    g.add_node("idea_refiner", idea_refiner)
    g.add_node("architect", architect)
    g.add_node("human_checkpoint", human_checkpoint)
    g.add_node("code_writer", code_writer)
    g.add_node("github_agent", github_agent)

    g.add_edge(START, "idea_refiner")
    g.add_edge("idea_refiner", "architect")
    g.add_edge("architect", "human_checkpoint")
    g.add_conditional_edges(
        "human_checkpoint", route_after_checkpoint, {"code_writer": "code_writer", END: END}
    )
    g.add_edge("code_writer", "github_agent")
    g.add_edge("github_agent", END)

    return g.compile(checkpointer=InMemorySaver())


def initial_state(user_input: str) -> AgentOSState:
    return {
        "user_input": user_input,
        "refined_spec": None,
        "architecture": None,
        "generated_code": {},
        "github_pr_url": None,
        "error_log": [],
        "current_agent": "",
        "human_approved": False,
    }


if __name__ == "__main__":
    from langgraph.types import Command

    graph = make_graph()
    config = {"configurable": {"thread_id": "demo-1"}}

    paused = graph.invoke(initial_state("a todo app with reminders"), config)
    print("=== paused at human checkpoint ===")
    print(paused["__interrupt__"][0].value)

    resumed = graph.invoke(Command(resume="approve"), config)
    print("=== resumed, final state ===")
    print(resumed)
