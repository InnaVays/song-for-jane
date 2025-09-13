from __future__ import annotations
from typing import Dict, Any
from pydantic import ValidationError
from app.llm import llm
from app.prompts import CRITIC_SYS
from app.state import Review
from app.state import AppState


CRITIC_USER_TMPL = """
Stanza k: {k}
Text:\n{stanza}
StyleRules:\n{style}
Quality checks (from plan):\n{quality}
Forbidden (taboo):\n{forbidden}
"""

def critic_node(state: AppState) -> Dict[str, Any]:
    k = len(state.get("stanzas", []))
    stanza = state["stanzas"][k - 1]
    style = state.get("style", {})
    quality = state.get("chosen_plan", {}).get("quality_checks", {})
    forbidden = style.get("forbidden", [])
    user = CRITIC_USER_TMPL.format(k=k, stanza=stanza, style=style, quality=quality, forbidden=forbidden)


    content = llm.json_call(
    tier="medium",
    system=CRITIC_SYS,
    user=user,
    temperature=0.15,
    max_output_tokens=600,
    )
    try:
        review = Review.model_validate_json(content)
    except ValidationError:
        # escalate once
        content = llm.json_call("large", CRITIC_SYS, user, 0.1)
        review = Review.model_validate_json(content)

    reviews = list(state.get("reviews", []))
    reviews.append(review.model_dump())

    # severity gate for decider
    sev = review.severity_max
    return {"reviews": reviews, "last_decision": "rewrite" if sev in {"critical", "major"} else "accept"}