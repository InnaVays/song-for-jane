from __future__ import annotations
from typing import Dict, Any
from app.llm import llm
from app.prompts import POEM_WRITER_SYS

from typing import List
from app.state import AppState


def _simple_last_word(line: str) -> str:
    line = line.strip().lower()
    parts = [p for p in line.split() if p]
    return parts[-1] if parts else ""


def _ends_rhyme(a: str, b: str) -> bool:
    a, b = a[-3:], b[-3:]
    if not a or not b:
        return True
    return a == b or a[-2:] == b[-2:]

def check_rhyme_scheme(text: str, scheme: str) -> bool:
    lines = [l for l in (s.strip() for s in text.splitlines()) if l]
    if len(lines) < 4:
        return True
    ends = [_simple_last_word(l) for l in lines[:4]]
    scheme = (scheme or "ABAB").upper()
    if scheme == "ABAB":
        return _ends_rhyme(ends[0], ends[2]) and _ends_rhyme(ends[1], ends[3])
    if scheme == "AABB":
        return _ends_rhyme(ends[0], ends[1]) and _ends_rhyme(ends[2], ends[3])
    if scheme == "ABBA":
        return _ends_rhyme(ends[0], ends[3]) and _ends_rhyme(ends[1], ends[2])

    return True

def _contains_taboo(text: str, taboo: List[str]) -> bool:
    t = text.lower()
    return any(w.lower() in t for w in taboo)


def check_rhyme_scheme(text: str, scheme: str) -> bool:
    # naive checker: ensure line endings repeat pattern letters count
    lines = [l.strip() for l in text.strip().splitlines() if l.strip()]
    if len(lines) < 4:
        return True # be lenient for short drafts
    # Only a placeholder heuristic; real checker can be added later
    return True

def poem_writer_node(state: AppState) -> Dict[str, Any]:
    k = len(state.get("stanzas", [])) + 1
    plan = state["chosen_plan"]
    style = state["style"]
    evidence = state.get("evidence", {})
    beat_k = None
    for b in plan.get("beats", []):
        if b.get("k") == k:
            beat_k = b
            break
    scheme = style.get("rhyme_policy", {}).get("scheme", "ABAB")

    user = (
        f"Stanza index: {k}\n"
        f"Beat: {beat_k}\n"
        f"Plan constraints: form={plan.get('form',{}).get('value')}, meter={plan.get('meter',{}).get('value')}\n"
        f"StyleRules: {style}\n"
        f"Evidence (hints): {evidence.get('beat_hints',{}).get(str(k),{})}\n"
        "Return stanza only.\n"
        )


    text = llm.text_call(
        tier="medium",
        system=POEM_WRITER_SYS,
        user=user,
        temperature=0.65,
        max_output_tokens=320,
        )

    # enforce taboo + rhyme quick-fix
    scheme = style.get("rhyme_policy", {}).get("scheme", "ABAB")
    taboo = list(style.get("forbidden", []))
    if _contains_taboo(text, taboo) or not check_rhyme_scheme(text, scheme):
        patch_prompt = (
        "Revise the stanza to strictly avoid forbidden words and follow rhyme scheme "
        f"{scheme}. Keep persona voice and concrete imagery."
        f"Forbidden: {taboo}"
        f"Stanza: {text}"
        )
        text = llm.text_call(
            tier="small",
            system="You carefully revise poetry with minimal edits to match constraints.",
            user=patch_prompt,
            temperature=0.3,
            max_output_tokens=320,
        )


    stanzas = list(state.get("stanzas", []))
    stanzas.append(text.strip())
    visible = {"k": k, "text": text.strip()}
    return {"stanzas": stanzas, "visible_stanza": visible}
