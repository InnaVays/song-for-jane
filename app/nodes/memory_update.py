from __future__ import annotations
from typing import Dict, Any, List
import json
from pathlib import Path
import chromadb
from openai import OpenAI
import os
import hashlib



def memory_update_node(state: Dict[str, Any]) -> Dict[str, Any]:
    fb = state.get("feedback_record", {})
    if not fb:
        return {}


    # Append to memory_items.jsonl (normalized lite)
    mem_dir = Path("memory")
    mem_dir.mkdir(parents=True, exist_ok=True)
    items_path = mem_dir / "memory_items.jsonl"


    items: List[dict] = []
    for s in fb.get("like", []) or []:
        items.append({"type":"taste","text":str(s),"meta":{"source":"feedback","tags":["like"]}})
    for s in (fb.get("targets", {}).get("imagery", {}).get("ban", []) or []):
        items.append({"type":"taboo","text":str(s),"meta":{"source":"feedback","tags":["imagery:ban"]}})
    for s in (fb.get("targets", {}).get("imagery", {}).get("add", []) or []):
        items.append({"type":"taste","text":str(s),"meta":{"source":"feedback","tags":["imagery:add"]}})
    # write
    with items_path.open("a", encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")


    # Embed & upsert into Chroma memory collection
    if items:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        texts = [it["text"] for it in items]
        resp = client.embeddings.create(model="text-embedding-3-small", input=texts)
        vecs = [d.embedding for d in resp.data]
        vdb = chromadb.PersistentClient(path="vectorstores/memory")
        col = vdb.get_collection("memory")
        ids = [hashlib.sha256((it["type"]+it["text"]).encode()).hexdigest() for it in items]
        col.add(documents=texts, embeddings=vecs, ids=ids, metadatas=[it.get("meta", {}) | {"type": it["type"]} for it in items])


    # Update preference_profile (very light)
    profile = state.get("preference_profile", {})
    for w in fb.get("targets", {}).get("imagery", {}).get("add", []) or []:
        profile.setdefault("imagery_boost", []).append(w)
    for w in fb.get("targets", {}).get("imagery", {}).get("ban", []) or []:
        profile.setdefault("taboo", []).append(w)


    # Persist profile cache
    Path("runs").mkdir(parents=True, exist_ok=True)
    (Path("runs")/"preference_profile.json").write_text(json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8")


    return {"preference_profile": profile}