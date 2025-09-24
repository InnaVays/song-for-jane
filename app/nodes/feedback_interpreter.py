from __future__ import annotations
from typing import Dict, Any
from app.llm import llm


FB_SYS = (
"Map raw feedback to FeedbackRecord JSON: like[], dislike[], targets{imagery{add[],ban[]}, tempo, persona{lock,id}, taboo_add[]}."
)


def feedback_interpreter_node(state: Dict[str, Any]) -> Dict[str, Any]:
    raw = state.get("raw_feedback", "ACCEPT")
    content = llm.json_call("small", FB_SYS, str(raw), 0.2, 500)
    import json
    try:
        fb = json.loads(content)
    except Exception:
        fb = {"like": [], "dislike": [], "targets": {}}
    return {"feedback_record": fb}