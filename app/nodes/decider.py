from __future__ import annotations
from typing import Dict, Any
from app.state import AppState

def decider_node(state: AppState) -> Dict[str, Any]:
    decision = state.get("last_decision", "accept")
    # Graph wiring handles routing; here we just expose flag
    return {"last_decision": decision}