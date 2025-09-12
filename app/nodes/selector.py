from __future__ import annotations
from typing import Dict, Any, List
from app.state import AppState


def _score(plan: Dict[str, Any], profile: Dict[str, Any]) -> float:
    score = 0.0
    rhyme_pref = profile.get("rhyme", {})
    meter_pref = profile.get("meter", {})
    persona_pref = profile.get("persona", {})
    taboo = set(profile.get("taboo", []))

    rhyme = plan.get("rhyme", {}).get("value")
    meter = plan.get("meter", {}).get("value")
    persona = plan.get("persona", {}).get("value")

    score += rhyme_pref.get(rhyme, 0.0)
    score += meter_pref.get(meter, 0.0)
    score += persona_pref.get(persona, 0.0)

    # penalize forbidden words in quality_checks
    forb = set(plan.get("quality_checks", {}).get("forbidden_words", []))
    if taboo & forb:
        score -= 1.0
    return score

def selector_node(state: AppState) -> Dict[str, Any]:
    variants: List[Dict[str, Any]] = state.get("plan_variants", [])
    profile = state.get("preference_profile", {})
    if not variants:
        return {}
    scored = sorted(((v, _score(v, profile)) for v in variants), key=lambda x: x[1], reverse=True)
    chosen, _ = scored[0]
    alts = [v for v, s in scored[1:2]] # keep one alt
    reason = "auto-score with preference profile"
    
    return {"chosen_plan": chosen, "alts": alts, "selection_reason": reason}