from __future__ import annotations
from typing import Dict, Any, Tuple, List
import chromadb
import re
from collections import Counter


def _fetch(col, query: str, n: int, where: dict | None = None) -> Tuple[List[str], List[dict]]:
    where = where or {}
    res = col.query(query_texts=[query], n_results=n, where=where)
    return res.get("documents", [[]])[0], res.get("metadatas", [[]])[0]

def micro_fetch_node(state: Dict[str, Any]) -> Dict[str, Any]:
    rp = state["retrieval_plan"]
    pros = chromadb.PersistentClient(path="vectorstores/prosody").get_collection("prosody")
    mem = chromadb.PersistentClient(path="vectorstores/memory").get_collection("memory")
    # User docs can be stored inside memory as type=exemplar/taste; keep same collection for demo
    docs = mem

    packs = {}
    for key in ("A", "B"):
        plan = rp[key]
        q = plan["query"]
        topk = int(plan["topk"])
        order = plan["priority"]
        hits = []
        for src in order:
            if src == "memory":
                d, m = _fetch(mem, q, topk, where=None)
            elif src == "user_docs":
                d, m = _fetch(docs, q + " user_docs", topk, where=None)
            else:
                d, m = _fetch(pros, q + " prosody", topk, where=None)
            for i in range(len(d)):
                hits.append((d[i], m[i]))
        # Build MicroPack
        taboo, exemplars, lex = [], [], []
        for doc, meta in hits:
            t = (meta or {}).get("type")
            if t == "taboo":
                taboo.append(doc[:80])
            elif t in {"exemplar", "taste"}:
                exemplars.append(doc[:220])
            # crude lexicon

        tokens = re.findall(r"[a-zA-Z']+", " ".join(exemplars).lower())
        freq = Counter(tokens)
        lex = [w for w,_ in freq.most_common(12) if len(w) > 3][:10]
        packs[key] = {"taboo": list(dict.fromkeys(taboo))[:30], "exemplars": exemplars[:4], "lexicon": lex}

    return {"micro_pack": packs}

