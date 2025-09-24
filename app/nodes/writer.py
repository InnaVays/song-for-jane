from __future__ import annotations
from typing import Dict, Any, List
from app.llm import llm


WRITER_SYS = (
"Write stanza k per Style and Plan (rhyme/meter). Use exactly one vivid concrete image. "
"Avoid taboo words. Output stanza only."
)

def _contains_taboo(text: str, taboo: List[str]) -> bool:
    t = text.lower()
    return any(w.lower() in t for w in taboo)




def writer_node(state: Dict[str, Any]) -> Dict[str, Any]:
    plan, style = state["plan"], state["style"]
    k = len(state.get("stanzas", [])) + 1
    beat = next((b for b in plan.get("beats", []) if b.get("k") == k), None)
    chosen = state.get("chosen_context", "A")
    pack = (state.get("micro_pack", {}).get(chosen) or {})
    taboo = list(set(style.get("forbidden", []) + pack.get("taboo", [])))


    user = (
    f"Stanza index: {k}\nPlan: rhyme={plan.get('rhyme')}, meter={plan.get('meter')}, persona={plan.get('persona')}\n"
    f"Beat: {beat}\nStyle: {style}\nContext(exemplars): {pack.get('exemplars', [])}\nTaboo: {taboo}\n"
    "Return stanza only."
    )
    text = llm.text_call("medium", WRITER_SYS, user, 0.6, 320)


    # guards
    if _contains_taboo(text, taboo) or len(text.split()) > state.get("toolcard", {}).get("writer", {}).get("max_len", 140):
        patch = (
        f"Revise stanza to avoid taboo and respect max length. Taboo={taboo}. Stanza:\n{text}"
        )
        text = llm.text_call("small", "Minimal editor for constraints.", patch, 0.3, 300)


    stanzas = list(state.get("stanzas", []))
    stanzas.append(text.strip())
    return {"stanzas": stanzas, "visible_stanza": {"k": k, "text": text.strip()}}

