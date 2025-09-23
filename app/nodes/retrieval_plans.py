from __future__ import annotations
from typing import Dict, Any


def retrieval_plans_node(state: Dict[str, Any]) -> Dict[str, Any]:
    plan = state["plan"]
    k = len(state.get("stanzas", [])) + 1
    beat = next((b for b in plan.get("beats", []) if b.get("k") == k), {"goal":"","image":"","turn":""})
    persona = plan.get("persona", "")
    # A/B tiny recipes
    A = {
    "priority": ["memory", "user_docs", "prosody"],
    "query": f"persona:{persona} goal:{beat.get('goal')} image:{beat.get('image')} recent",
    "topk": state.get("toolcard", {}).get("retrieval", {}).get("topk", 6)
    }
    B = {
    "priority": ["user_docs", "memory", "prosody"],
    "query": f"persona:{persona} rare imagery pitfalls avoid cliche",
    "topk": max(4, int(A["topk"]))
    }
    return {"retrieval_plan": {"A": A, "B": B}}