from llm import call_llm
from state import AgentOSState


def code_writer(state: AgentOSState) -> dict:
    prompt = (
        "Given this architecture, generate a minimal working code skeleton. "
        "Output ONLY file blocks in this exact format, one per file:\n"
        "### path/to/file\n<file content>\n\n"
        f"Architecture: {state['architecture']['raw']}"
    )
    raw = call_llm(prompt)

    files: dict[str, str] = {}
    current_path = None
    buf: list[str] = []
    for line in raw.splitlines():
        if line.startswith("### "):
            if current_path:
                files[current_path] = "\n".join(buf).strip()
            current_path = line[4:].strip()
            buf = []
        else:
            buf.append(line)
    if current_path:
        files[current_path] = "\n".join(buf).strip()
    if not files:
        files["GENERATED.md"] = raw

    return {"generated_code": files, "current_agent": "code_writer"}
