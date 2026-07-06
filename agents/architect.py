from llm import call_llm
from state import AgentOSState


def architect(state: AgentOSState) -> dict:
    prompt = (
        "Design a minimal architecture for this spec: tech stack, file "
        "structure, and a short db schema section if data is involved.\n\n"
        f"Spec: {state['refined_spec']['raw']}"
    )
    arch_text = call_llm(prompt)
    return {"architecture": {"raw": arch_text}, "current_agent": "architect"}
