from __future__ import annotations
from typing import Dict, Any


def finalize_node(state: Dict[str, Any]) -> Dict[str, Any]:
    stanzas = state.get("stanzas", []) or []
    return {"final_text": "\n\n".join(stanzas)}