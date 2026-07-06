from typing import TypedDict


class AgentOSState(TypedDict):
    user_input: str
    refined_spec: dict | None       # idea_refiner output
    architecture: dict | None       # architect output (includes db schema section)
    generated_code: dict[str, str]  # path → file content
    github_pr_url: str | None
    error_log: list[str]
    current_agent: str
    human_approved: bool
