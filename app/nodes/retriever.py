from __future__ import annotations
from typing import Dict, Any
from app.state import AppState, Evidence
from app.llm import llm
from app.prompts import RETRIEVER_SYS
import json


RETRIEVE_USER_TMPL = """
Chosen plan (JSON):
{plan}

Produce compact evidence JSON.
"""

def retriever_node(state: AppState) -> Dict[str, Any]:
    plan = state["chosen_plan"]
    user = RETRIEVE_USER_TMPL.format(plan=plan)
    content = llm.json_call(
        tier="small",
        system=RETRIEVER_SYS,
        user=user,
        temperature=0.15,
        max_output_tokens=900,
        )
    data = json.loads(content)
    ev = Evidence(**data)
    
    return {"evidence": ev.model_dump()}