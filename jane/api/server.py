from __future__ import annotations

from fastapi import FastAPI, Depends
from jane.schemas import ChatRequest, ChatResponse
from jane.api.deps import build_router
from jane.router import Router

app = FastAPI(title="Jane Demo API")

def get_router() -> Router:
    # simple DI wrapper
    return build_router()

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, router: Router = Depends(get_router)) -> ChatResponse:
    """
    Entry point for chat messages.
    Delegates to Router (intent + dispatch).
    """
    return router.route(req)

@app.post("/feedback")
def feedback(trace_id: str, vote: int, comment: str = "", router: Router = Depends(get_router)) -> dict:
    """
    Collect user feedback on a specific trace. No-op for now; will write to MemoryStore later.
    """
    # Example (future): router.memory.append_event(...)
    return {"ok": True}

@app.post("/train/lora")
def train_lora() -> dict:
    """
    Placeholder endpoint to kick off LoRA training on accumulated user data.
    """
    return {"ok": True, "msg": "LoRA training stub"}
