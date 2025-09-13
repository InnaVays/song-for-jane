from __future__ import annotations
from typing import Dict, Any
from pydantic import ValidationError
from app.llm import llm
from app.prompts import FEEDBACK_INTERPRETER_SYS
from app.state import FeedbackRecord
from app.state import AppState


FB_USER_TMPL = """
Current plan (for reference):
{plan}
Current style:
{style}
User feedback (raw):
{feedback}
"""

def feedback_interpreter_node(state: AppState) -> Dict[str, Any]:
    raw_fb = state.get("raw_feedback", "like: faster rhythm; dislike: cliché 'broken heart'")
    plan = state.get("chosen_plan", {})
    style = state.get("style", {})
    user = FB_USER_TMPL.format(plan=plan, style=style, feedback=raw_fb)


    content = llm.json_call(
    tier="small",
    system=FEEDBACK_INTERPRETER_SYS,
    user=user,
    temperature=0.2,
    max_output_tokens=500,
    )
    try:
        fb = FeedbackRecord.model_validate_json(content)
    except ValidationError:
        content = llm.json_call("small", FEEDBACK_INTERPRETER_SYS, user, 0.1)
        fb = FeedbackRecord.model_validate_json(content)
    return {"feedback_record": fb.model_dump()}