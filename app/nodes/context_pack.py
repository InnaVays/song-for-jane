from __future__ import annotations
from typing import Dict, Any, List
import chromadb

from app.llm import llm
import re
from collections import Counter
import json

CTX_SYS = (
"Compress retrieval hits into JSON sections with strict caps. Keys: "
"taboo[], exemplars[], user_lexicon[], theory_rules, template_digest."
)

def _search(col, query: str, top_k: int = 8, where: dict | None = None):
    where = where or {}
    res = col.query(query_texts=[query], n_results=top_k, where=where)
    docs = res.get("documents", [[]])[0]
    metas = res.get("metadatas", [[]])[0]
    return list(zip(docs, metas))

def context_pack_node(state: Dict[str, Any]) -> Dict[str, Any]:
    client = chromadb.PersistentClient(path="vectorstores/memory")
    mem = client.get_collection("memory")
    pros = chromadb.PersistentClient(path="vectorstores/prosody").get_collection("prosody")

    # Simple hybrid: pull some taboo & exemplars from memory; brief/topic as query
    brief_text = state["brief"].get("raw_user_message", "rock ballad")
    mem_hits = _search(mem, brief_text, 8)
    pros_hits = _search(pros, "prosody ballad rhyme meter pitfalls", 8)

    # Build raw pack (light heuristics)
    taboo = []
    exemplars = []
    for doc, meta in mem_hits:
        t = (meta or {}).get("type")
        if t == "taboo":
            taboo.append(doc[:200])
        elif t in {"exemplar", "taste"}:
            exemplars.append(doc[:220])
    user_lex = []
    # naive n-grams from exemplars

    tokens = re.findall(r"[a-zA-Z']+", " ".join(exemplars).lower())

    freq = Counter(tokens)
    user_lex = [w for w,_ in freq.most_common(12) if len(w) > 3][:10]

    # theory digest from prosody
    theory_rules = [d[:220] for d,_ in pros_hits[:6]]

    raw = {
    "taboo": list(dict.fromkeys(taboo))[:30],
    "exemplars": exemplars[:6],
    "user_lexicon": user_lex,
    "theory_rules": theory_rules,
    "template_digest": "rock_ballad.expert.yaml (digest TBD)",
    }


    # Optionally compress via small model (kept simple; could skip)

    user = json.dumps(raw, ensure_ascii=False)
    content = llm.json_call("small", CTX_SYS, user, 0.2, 700)
    try:
        pack = json.loads(content)
    except Exception:
        pack = raw
    return {"global_pack": pack}