# app/nodes/brief.py
from __future__ import annotations
from typing import Dict, Any
import json

from app.state import AppState
from app.llm import llm

BRIEF_SYS = (
    "Extract a normalized brief for lyric writing. "
    "Return JSON with keys: raw_user_message, language, persona_request, "
    "must_include[], must_avoid[], length_request, notes."
)

def _coerce_brief(d: Dict[str, Any], fallback_raw: str) -> Dict[str, Any]:
    """Ensure required keys exist with sane defaults."""
    return {
        "raw_user_message": d.get("raw_user_message", fallback_raw),
        "language": d.get("language", "en"),
        "persona_request": d.get("persona_request"),
        "must_include": d.get("must_include") or [],
        "must_avoid": d.get("must_avoid") or [],
        "length_request": d.get("length_request"),
        "notes": d.get("notes"),
    }

def brief_node(state: AppState) -> Dict[str, Any]:
    raw = (
        (state.get("brief") or {}).get("raw_user_message")
        or state.get("raw_user_message")
        or ""
    )
    user = raw if raw else "Write a rock ballad about city rain and late trains."

    # First attempt
    content = llm.json_call(
        tier="small",
        system=BRIEF_SYS,
        user=user,
        temperature=0.2,
        max_output_tokens=700,
    )

    def parse_or_retry(payload: str) -> Dict[str, Any]:
        try:
            data = json.loads(payload)
            if not isinstance(data, dict):
                raise ValueError("LLM did not return a JSON object")
            return data
        except Exception:
            # One low-temp retry
            payload2 = llm.json_call(
                tier="small",
                system=BRIEF_SYS,
                user=user,
                temperature=0.1,
                max_output_tokens=700,
            )
            try:
                data2 = json.loads(payload2)
                if not isinstance(data2, dict):
                    raise ValueError("LLM did not return a JSON object")
                return data2
            except Exception:
                # Final minimal fallback
                return {
                    "raw_user_message": user,
                    "language": "en",
                    "must_include": [],
                    "must_avoid": [],
                    "notes": None,
                }

    parsed = parse_or_retry(content)
    brief = _coerce_brief(parsed, user)
    return {"brief": brief}
