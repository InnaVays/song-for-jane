from __future__ import annotations
from typing import Dict, Any
from pydantic import ValidationError
from app.state import AppState
from app.llm import llm



BRIEF_SYS = (
"Extract a normalized brief for a rock ballad from raw user text. "
"Return strict JSON with keys: raw_user_message, topic, emotion, persona_request, language, length_request, "
"must_include[], must_avoid[], style_hints[], references_from_memory{likes[],dont[],best_ids[]}, user_docs_refs[], notes, completeness (0..1)."
)


def brief_node(state: AppState) -> Dict[str, Any]:
    raw = state.get("brief", {}).get("raw_user_message") or state.get("raw_user_message") or ""
    user = raw if raw else "Write a rock ballad about city rain and late trains."
    content = llm.json_call(
    tier="small",
    system=BRIEF_SYS,
    user=user,
    temperature=0.2,
    max_output_tokens=700,
    )
    try:
        parsed = Brief.model_validate_json(content)
    except ValidationError as e:
        # one retry with lower temperature
        content = llm.json_call(tier="small", system=BRIEF_SYS, user=user, temperature=0.1)
        parsed = Brief.model_validate_json(content)
    return {"brief": parsed.model_dump()}

