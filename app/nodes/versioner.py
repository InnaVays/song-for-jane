from __future__ import annotations
from typing import Dict, Any
from datetime import datetime

def versioner_node(state: Dict[str, Any]) -> Dict[str, Any]:
    log = list(state.get("version_log", []))
    v_from = f"v{len(log)}"
    v_to = f"v{len(log)+1}"
    diff = state.get("version_diff", "")
    fb = state.get("feedback_record", {})
    stanza_k = len(state.get("stanzas", []))
    why = {
        "timestamp": fb.get("timestamp") or datetime.utcnow().isoformat() + "Z",
        "reason": diff,
        "stanza_k": stanza_k,
        }
    log.append({"from": v_from, "to": v_to, "diff": diff, "why": why})
    return {"version_log": log}