from __future__ import annotations
from typing import Dict, Any
from app.llm import llm
import json, hashlib



PLANNER_SYS = (
    "You are MASTER PLANNER. Using the Brief + GlobalPack + TemplateDigest + ToolRegistry, "
    "output JSON with keys: plan, style, toolcard. Plan must include: form, rhyme, meter, stanza_count, persona, beats[{k,goal,image,turn}]. "
    "Style: diction[], syntax[], imagery[], forbidden[], meter_policy{target,tol}, rhyme_policy{scheme}. "
    "Toolcard: writer{max_len,vivid_images}, retrieval{topk}, ab_strategies{A,B}."
    )


TOOL_REGISTRY = {
    "triz": "micro-mutations on image/turn only",
    "retriever": "hybrid memory/user_docs/prosody",
    "writer": "draft then guards then mini_patch",
    }

def master_planner_node(state: Dict[str, Any]) -> Dict[str, Any]:
    brief = state["brief"]
    pack = state["global_pack"]
    key = hashlib.sha256(json.dumps({"brief":brief, "pack":pack}, sort_keys=True).encode()).hexdigest()
    state_cache = state.get("_planner_cache", {})
    if key in state_cache:
        return {"plan": state_cache[key]["plan"], "style": state_cache[key]["style"], "toolcard": state_cache[key]["toolcard"], "_planner_cache": state_cache}


    user = json.dumps({"brief": brief, "global_pack": pack, "tools": TOOL_REGISTRY}, ensure_ascii=False)
    content = llm.json_call("large", PLANNER_SYS, user, 0.35, 2200)
    try:
        data = json.loads(content)
        plan, style, toolcard = data["plan"], data["style"], data["toolcard"]
    except Exception:
        # Minimal fallback
        plan = {"form":"ballad","rhyme":"ABAB","meter":"iamb_4","stanza_count":4,"persona":"frontman","beats":[{"k":1,"goal":"set scene","image":"rain","turn":"choice"}]}
        style = {"diction":[],"syntax":[],"imagery":[],"forbidden":pack.get("taboo",[]),"meter_policy":{"target":"iamb_4","tol":"±1"},"rhyme_policy":{"scheme":"ABAB"},"persona_markers":[]}
        toolcard = {"writer":{"max_len":140,"vivid_images":1},"retrieval":{"topk":6},"ab_strategies":{"A":"exploit","B":"explore"}}
    state_cache[key] = {"plan": plan, "style": style, "toolcard": toolcard}
    return {"plan": plan, "style": style, "toolcard": toolcard, "_planner_cache": state_cache}

