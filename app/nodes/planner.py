from __future__ import annotations
from typing import Dict, Any
from pydantic import ValidationError
from app.state import AppState, PlanVariant
from app.llm import llm
from app.prompts import PLANNER_SYS
import json


PLANNER_USER_TMPL = """
Expert Template (YAML or JSON summary may be in context externally).
Normalized brief:
{brief}

Return JSON: {{"plan_variants": [ ... ]}}
"""

def planner_node(state: AppState) -> Dict[str, Any]:
    brief = state["brief"]
    user = PLANNER_USER_TMPL.format(brief=brief)
    content = llm.json_call(
        tier="large",
        system=PLANNER_SYS,
        user=user,
        temperature=0.35,
        max_output_tokens=2200,
        )
    data = __safe_json(content)
    variants = data.get("plan_variants", [])
    # Light validation per-item
    parsed = []
    for i, v in enumerate(variants):
        try:
            pv = PlanVariant(**v)
            parsed.append(pv.model_dump())
        except Exception:
            continue
    if not parsed:
        # fallback once with medium
        content = llm.json_call(tier="medium", system=PLANNER_SYS, user=user, temperature=0.2)
        data = __safe_json(content)
        for v in data.get("plan_variants", []):
            try:
                parsed.append(PlanVariant(**v).model_dump())
            except Exception:
                pass
    return {"plan_variants": parsed}

def __safe_json(text: str) -> Dict[str, Any]:
    try:
        return json.loads(text)
    except Exception:
        return {}

