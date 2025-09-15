# app/indexing/build_memory_index.py
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Dict, Tuple, Any

import chromadb
from chromadb import PersistentClient
from openai import OpenAI


# ============== Config ==============
@dataclass
class IngestConfig:
    memory_dir: Path
    persist_dir: Path
    collection: str = "memory"
    embedding_model: str = "text-embedding-3-small"
    batch_size: int = 64
    reset: bool = False


# ============== FS helpers ==============
def iter_jsonl(path: Path) -> Iterable[Dict[str, Any]]:
    if not path.exists():
        return
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except Exception:
                    # tolerate plain-string lines in likes/dont/best
                    yield {"text": line}
    except Exception as e:
        print(f"[WARN] Failed to read {path}: {e}", file=sys.stderr)


def sha_id(parts: List[str]) -> str:
    m = hashlib.sha256()
    for p in parts:
        m.update((p or "").encode("utf-8"))
        m.update(b"|")
    return m.hexdigest()


# ============== Normalization ==============
def _mk_item(
    itype: str,
    text: str,
    meta: Dict[str, Any],
    base_id_parts: List[str],
) -> Dict[str, Any]:
    text = (text or "").strip()
    if not text:
        return {}
    iid = sha_id(base_id_parts + [itype, text])
    return {
        "id": iid,
        "type": itype,
        "text": text,
        "meta": meta,
    }


def from_likes_jsonl(path: Path) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    for row in iter_jsonl(path):
        text = row.get("text") if isinstance(row, dict) else None
        if not text and isinstance(row, str):
            text = row
        if not text:
            continue
        meta = {"source": path.name, "tags": ["like"]}
        items.append(_mk_item("taste", text, meta, [str(path)]))
    return items


def from_dont_jsonl(path: Path) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    for row in iter_jsonl(path):
        text = row.get("text") if isinstance(row, dict) else None
        if not text and isinstance(row, str):
            text = row
        if not text:
            continue
        meta = {"source": path.name, "tags": ["ban"]}
        items.append(_mk_item("taboo", text, meta, [str(path)]))
    return items


def from_best_jsonl(path: Path) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    for row in iter_jsonl(path):
        text = row.get("text") if isinstance(row, dict) else None
        if not text and isinstance(row, str):
            text = row
        if not text:
            continue
        meta = {"source": path.name, "tags": ["best", "exemplar"]}
        items.append(_mk_item("exemplar", text, meta, [str(path)]))
    return items


def _push_if(items: List[Dict[str, Any]], maybe: Dict[str, Any]):
    if maybe and maybe.get("text"):
        items.append(maybe)


def from_feedback_jsonl(path: Path) -> List[Dict[str, Any]]:
    """
    FeedbackRecord lines:
      {
        "timestamp": "...",
        "like": ["..."],
        "dislike": ["..."],
        "targets": {
            "imagery": {"add": ["..."], "ban": ["..."]},
            "meter": {"prefer": "iamb_3", "tolerance": "±1"},
            "persona": {"lock": true, "id": "frontman"}
        },
        "examples": {"user_like_snippet": "..."}
      }
    """
    items: List[Dict[str, Any]] = []
    for row in iter_jsonl(path):
        if not isinstance(row, dict):
            continue
        ts = row.get("timestamp")
        base_parts = [str(path), ts or ""]
        meta_base = {"source": path.name, "timestamp": ts} if ts else {"source": path.name}

        # likes
        for s in (row.get("like") or []):
            _push_if(
                items,
                _mk_item("taste", str(s), {**meta_base, "tags": ["like"]}, base_parts),
            )
        # dislikes (store as taste with 'dislike' tag to bias away)
        for s in (row.get("dislike") or []):
            _push_if(
                items,
                _mk_item("taste", f"DISLIKE: {str(s)}", {**meta_base, "tags": ["dislike"]}, base_parts),
            )
        # imagery add/ban
        tgt = row.get("targets") or {}
        img = (tgt.get("imagery") or {})
        for s in img.get("add", []) or []:
            _push_if(
                items,
                _mk_item("taste", str(s), {**meta_base, "tags": ["imagery:add"]}, base_parts),
            )
        for s in img.get("ban", []) or []:
            _push_if(
                items,
                _mk_item("taboo", str(s), {**meta_base, "tags": ["imagery:ban"]}, base_parts),
            )
        # persona lock/pref
        persona = tgt.get("persona") or {}
        if persona.get("id"):
            text = f"persona:{persona.get('id')}"
            tags = ["persona:lock"] if persona.get("lock") else ["persona:pref"]
            _push_if(
                items,
                _mk_item("persona_pref", text, {**meta_base, "tags": tags}, base_parts),
            )
        # meter prefer
        meter = tgt.get("meter") or {}
        if meter.get("prefer"):
            text = f"meter:{meter['prefer']} tol:{meter.get('tolerance','')}"
            _push_if(
                items,
                _mk_item("note", text, {**meta_base, "tags": ["meter:prefer"]}, base_parts),
            )
        # example
        ex = (row.get("examples") or {}).get("user_like_snippet")
        if ex:
            _push_if(items, _mk_item("exemplar", str(ex), {**meta_base, "tags": ["example"]}, base_parts))
    return items


def from_memory_items_jsonl(path: Path) -> List[Dict[str, Any]]:
    """
    Already-normalized items:
      { "id": "...", "type":"taste|taboo|exemplar|note|plan_diff|persona_pref", "text": "...", "meta": {...} }
    """
    out: List[Dict[str, Any]] = []
    for row in iter_jsonl(path):
        if not isinstance(row, dict):
            continue
        iid = row.get("id") or sha_id([str(path), row.get("type", ""), row.get("text", "")])
        typ = row.get("type") or "note"
        text = (row.get("text") or "").strip()
        meta = row.get("meta") or {}
        if not text:
            continue
        out.append({"id": iid, "type": typ, "text": text, "meta": meta})
    return out


def load_all_memory_items(memory_dir: Path) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    likes = memory_dir / "likes.jsonl"
    dont = memory_dir / "dont.jsonl"
    best = memory_dir / "best.jsonl"
    feedback = memory_dir / "feedback.jsonl"
    normalized = memory_dir / "memory_items.jsonl"

    if likes.exists():
        items.extend(from_likes_jsonl(likes))
    if dont.exists():
        items.extend(from_dont_jsonl(dont))
    if best.exists():
        items.extend(from_best_jsonl(best))
    if feedback.exists():
        items.extend(from_feedback_jsonl(feedback))
    if normalized.exists():
        items.extend(from_memory_items_jsonl(normalized))

    # Dedup lexically by (type,text) to keep index small; merge tags if duplicates
    dedup: Dict[Tuple[str, str], Dict[str, Any]] = {}
    for it in items:
        if not it or not it.get("text"):
            continue
        key = (it.get("type", ""), it.get("text", ""))
        if key not in dedup:
            dedup[key] = it
        else:
            # merge tags
            t1 = set((dedup[key].get("meta") or {}).get("tags", []) or [])
            t2 = set((it.get("meta") or {}).get("tags", []) or [])
            meta = {**(dedup[key].get("meta") or {})}
            meta["tags"] = sorted(t1 | t2)
            dedup[key]["meta"] = meta

    # assign stable ids after dedup
    final: List[Dict[str, Any]] = []
    for (typ, text), it in dedup.items():
        meta = it.get("meta") or {}
        iid = it.get("id") or sha_id([typ, text, json.dumps(meta, ensure_ascii=False, sort_keys=True)])
        final.append({"id": iid, "type": typ, "text": text, "meta": meta})
    return final


# ============== Embeddings ==============
def embed_batches(
    client: OpenAI,
    model: str,
    texts: List[str],
    batch_size: int,
) -> List[List[float]]:
    vecs: List[List[float]] = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        resp = client.embeddings.create(model=model, input=batch)
        vecs.extend([d.embedding for d in resp.data])
    return vecs


# ============== Chroma helpers ==============
def get_collection(client: PersistentClient, name: str):
    try:
        return client.get_collection(name)
    except Exception:
        return client.create_collection(name)


# ============== Ingest main ==============
def ingest(config: IngestConfig) -> None:
    if config.reset and config.persist_dir.exists():
        print(f"[INFO] Resetting vectorstore at {config.persist_dir}")
        shutil.rmtree(config.persist_dir, ignore_errors=True)

    config.persist_dir.mkdir(parents=True, exist_ok=True)

    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        print("[ERROR] OPENAI_API_KEY is not set. See .env.example", file=sys.stderr)
        sys.exit(1)

    items = load_all_memory_items(config.memory_dir)
    if not items:
        print(f"[WARN] No memory items found in {config.memory_dir}")
        return

    texts = [it["text"] for it in items]
    ids = [it["id"] for it in items]
    metadatas = []
    for it in items:
        meta = dict(it.get("meta") or {})
        meta["type"] = it.get("type")
        # convenience: put text in metadata too for quick scans (optional)
        meta.setdefault("preview", it["text"][:160])
        metadatas.append(meta)

    print(f"[INFO] Memory items: {len(items)}. Embedding with {config.embedding_model}…")
    oai = OpenAI(api_key=openai_key)
    vectors = embed_batches(oai, config.embedding_model, texts, config.batch_size)

    vdb = chromadb.PersistentClient(path=str(config.persist_dir))
    col = get_collection(vdb, config.collection)

    print(f"[INFO] Upserting into Chroma at {config.persist_dir} (collection: {config.collection})…")
    col.add(documents=texts, embeddings=vectors, ids=ids, metadatas=metadatas)

    print("[OK] Memory ingest complete.")
    print(f"  Items: {len(items)}")
    print(f"  Store: {config.persist_dir}")
    print(f"  Coll.: {config.collection}")


# ============== CLI ==============
def parse_args() -> IngestConfig:
    ap = argparse.ArgumentParser(description="Build User Memory index → Chroma vectorstore")
    ap.add_argument(
        "--memory",
        type=str,
        default="memory",
        help="Path to memory folder (likes.jsonl, dont.jsonl, best.jsonl, feedback.jsonl, memory_items.jsonl)",
    )
    ap.add_argument(
        "--persist",
        type=str,
        default="vectorstores/memory",
        help="Path to persistent Chroma directory",
    )
    ap.add_argument(
        "--collection",
        type=str,
        default="memory",
        help="Chroma collection name",
    )
    ap.add_argument(
        "--model",
        type=str,
        default="text-embedding-3-small",
        help="OpenAI embedding model id",
    )
    ap.add_argument(
        "--batch-size",
        type=int,
        default=64,
        help="Embedding batch size",
    )
    ap.add_argument(
        "--reset",
        action="store_true",
        help="Delete the existing persist dir before building",
    )
    args = ap.parse_args()

    return IngestConfig(
        memory_dir=Path(args.memory).resolve(),
        persist_dir=Path(args.persist).resolve(),
        collection=args.collection,
        embedding_model=args.model,
        batch_size=args.batch_size,
        reset=bool(args.reset),
    )


if __name__ == "__main__":
    cfg = parse_args()
    print(
        f"[RUN] memory={cfg.memory_dir} → persist={cfg.persist_dir} "
        f"(collection={cfg.collection}, model={cfg.embedding_model})"
    )
    ingest(cfg)
