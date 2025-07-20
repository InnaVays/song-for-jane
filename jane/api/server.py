from fastapi import FastAPI
from jane.schemas import ChatRequest, ChatResponse

app = FastAPI(title="Jane Demo API")

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    """
    Entry point for chat messages.
    Delegates to Router (wired elsewhere via DI in real app).
    """
    raise NotImplementedError

@app.post("/feedback")
def feedback(trace_id: str, vote: int, comment: str = "") -> dict:
    """
    Collect user feedback on a specific trace. Non-blocking.
    """
    raise NotImplementedError

@app.post("/train/lora")
def train_lora() -> dict:
    """
    Placeholder endpoint to kick off LoRA training on accumulated user data.
    """
    raise NotImplementedError
