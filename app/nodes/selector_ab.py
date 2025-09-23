from __future__ import annotations
from typing import Dict, Any

def _score(pack: dict, persona: str, recent_taboo: set[str]) -> float:
    s = 0.0
    # fewer taboo = better
    s += max(0, 10 - len(pack.get("taboo", []))) * 0.1
    # some lexicon coverage
    s += min(len(pack.get("lexicon", [])), 8) * 0.05
    # persona not used directly here; stub for future
    return s

def selector_ab_node(state: Dict[str, Any]) -> Dict[str, Any]:
    packs = state.get("micro_pack", {})
    persona = state.get("plan", {}).get("persona", "")
    recent_taboo = set(state.get("style", {}).get("forbidden", []))
    a = _score(packs.get("A", {}), persona, recent_taboo)
    b = _score(packs.get("B", {}), persona, recent_taboo)
    chosen = "A" if a >= b else "B"
    return {"chosen_context": chosen}