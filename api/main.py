from fastapi import FastAPI
from langgraph.types import Command
from pydantic import BaseModel

from orchestrator import initial_state, make_graph

app = FastAPI()
graph = make_graph()


class RunRequest(BaseModel):
    idea: str
    thread_id: str = "default"


class ApproveRequest(BaseModel):
    thread_id: str
    decision: str


@app.post("/run")
def run(req: RunRequest):
    config = {"configurable": {"thread_id": req.thread_id}}
    result = graph.invoke(initial_state(req.idea), config)
    if "__interrupt__" in result:
        return {"status": "paused_for_approval", "payload": result["__interrupt__"][0].value}
    return {"status": "done", "result": result}


@app.post("/approve")
def approve(req: ApproveRequest):
    config = {"configurable": {"thread_id": req.thread_id}}
    result = graph.invoke(Command(resume=req.decision), config)
    return {"status": "done", "result": result}
