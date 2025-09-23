from __future__ import annotations
from typing import Dict, Any
from pathlib import Path
import os, sys, subprocess

def _ensure_store(kind: str, build_script: str, args: list[str]) -> None:
    base = Path(f"vectorstores/{kind}")
    if not base.exists() or not any(base.iterdir()):
        print(f"[INIT] Building {kind} index…")
        subprocess.check_call([sys.executable, build_script, *args])

def bootstrap_node(state: Dict[str, Any]) -> Dict[str, Any]:
    # Ensure vectorstores for prosody + memory
    _ensure_store("prosody", "app/indexing/build_kb_index.py", ["--source", "kb/prosody_corpus", "--persist", "vectorstores/prosody", "--collection", "prosody"])
    _ensure_store("memory", "app/indexing/build_memory_index.py", ["--memory", "memory", "--persist", "vectorstores/memory", "--collection", "memory"])
    # Load preference profile if present
    pref_path = Path("runs/preference_profile.json")
    profile = {}
    if pref_path.exists():
        import json
        profile = json.loads(pref_path.read_text(encoding="utf-8"))
    return {"ready": True, "preference_profile": profile}