# app/nodes/show_to_user.py
from __future__ import annotations
from typing import Dict, Any

def show_to_user_node(state: Dict[str, Any]) -> Dict[str, Any]:
    k = len(state.get("stanzas", []))
    vis = state.get("visible_stanza", {"k": k, "text": state["stanzas"][-1] if k else ""})
    out = {
        "awaiting_feedback": True,
        "visible_stanza": vis,
        "feedback_prompt": "Что изменить? Ритм, образ, рифма, табу-слова, персона, тон.",
    }
    return out