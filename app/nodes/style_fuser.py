from __future__ import annotations
from typing import Dict, Any
from pydantic import ValidationError
from app.state import AppState, StyleRules
from app.llm import llm
from app.prompts import STYLE_FUSER_SYS

STYLE_USER_TMPL = """
Chosen plan:
{plan}
Evidence:
{evidence}
Preference profile:
{profile}
"""

def style_fuser_node(state: AppState) -> Dict[str, Any]:
    plan = state["chosen_plan"]
    evidence = state.get("evidence", {})
    profile = state.get("preference_profile", {})
    user = STYLE_USER_TMPL.format(plan=plan, evidence=evidence, profile=profile)
    content = llm.json_call(
    tier="medium",
    system=STYLE_FUSER_SYS,
    user=user,
    temperature=0.25,
    max_output_tokens=900,
    )
    try:
        style = StyleRules.model_validate_json(content)
    except ValidationError:
        # retry cooler
        content = llm.json_call("medium", STYLE_FUSER_SYS, user, 0.1)
        style = StyleRules.model_validate_json(content)
    return {"style": style.model_dump()}

