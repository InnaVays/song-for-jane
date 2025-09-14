from __future__ import annotations
from typing import Dict, Any
from copy import deepcopy
from app.llm import llm
from app.prompts import REPLANNER_SYS
import json


REPLAN_USER_TMPL = """
FeedbackRecord:
{fb}
Current plan:
{plan}
Return JSON with the same plan structure and a 'diff_explain' field.
"""

def _preserve_locks(old: Dict[str, Any], new: Dict[str, Any]) -> Dict[str, Any]:
    out = deepcopy(new)
    for key in ["form", "rhyme", "meter", "stanza_count", "persona"]:
        try:
            if old.get(key, {}).get("locked"):
                out[key] = old[key]
        except Exception:
            pass
    return out

def _validate_plan(plan: Dict[str, Any]) -> bool:
    rp = plan.get("rhyme", {}).get("value")
    mp = plan.get("meter", {}).get("value")
    return rp in {"ABAB", "AABB", "ABBA"} and isinstance(mp, str)

def replanner_node(state: Dict[str, Any]) -> Dict[str, Any]:
    fb = state.get("feedback_record", {})
    plan = state.get("chosen_plan", {})
    user = REPLAN_USER_TMPL.format(fb=fb, plan=plan)
    content = llm.json_call(
        tier="medium",
        system=REPLANNER_SYS,
        user=user,
        temperature=0.2,
        max_output_tokens=1200,
        )
    data = json.loads(content)
    new_plan = _preserve_locks(plan, data)
    if not _validate_plan(new_plan):
        content = llm.json_call("large", REPLANNER_SYS, user, 0.1)
        data = json.loads(content)
        new_plan = _preserve_locks(plan, data)
    diff = data.get("diff_explain", "minimal changes applied")
    
    return {"chosen_plan": new_plan, "version_diff": diff}