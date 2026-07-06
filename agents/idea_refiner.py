from llm import call_llm
from state import AgentOSState


def idea_refiner(state: AgentOSState) -> dict:
    prompt = (
        "Turn this vague software idea into one scoped spec: feature list, "
        "target users, and explicit out-of-scope items. Plain text.\n\n"
        f"Idea: {state['user_input']}"
    )
    spec_text = call_llm(prompt)
    return {"refined_spec": {"raw": spec_text}, "current_agent": "idea_refiner"}
