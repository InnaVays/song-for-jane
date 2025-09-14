from __future__ import annotations
from typing import Dict, Any
from app.state import AppState

def memory_io_node(state: AppState) -> Dict[str, Any]:
    # Placeholder: wire to your vector store later. Keep interface stable.
    profile = state.get("preference_profile", {})
    # naive boost from last feedback
    fb = state.get("feedback_record", {})
    if fb:
        for w in fb.get("like", []):
            profile.setdefault("imagery_boost", []).append(w)
        for w in fb.get("targets", {}).get("imagery", {}).get("ban", []):
            profile.setdefault("taboo", []).append(w)
    return {"preference_profile": profile}