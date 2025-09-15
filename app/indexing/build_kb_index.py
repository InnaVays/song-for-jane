# app/indexing/build_kb_index.py
from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Dict, Tuple

import chromadb
from chromadb import PersistentClient
from openai import OpenAI


# --------- Config dataclasses ---------
@dataclass
class IngestConfig:
    source_dir: Path
    persist_dir: Path
    collection: str = "prosody"
    embedding_model: str = "text-embedding-3-small"
    chunk_size: int = 800
    chunk_overlap: int = 120
    batch_size: int = 64
    exts: Tuple[str, ...] = (".txt", ".md")
    reset: bool = False

# --------- I/O helpers ---------
def iter_files(root: Path, exts: Tuple[str, ...]) -> Iterable[Path]:
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in exts:
            yield p

def read_text_file(path: Path) -> str:
    try:
        # UTF-8 best-effort
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        print(f"[WARN] Failed to read {path}: {e}", file=sys.stderr)
        return ""

# --------- Chunking ---------
def chunk_text(text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
    """
    Simple, robust char-based chunker with overlap.
    Keeps boundaries on paragraph breaks when possible.
    """
    text = text.strip()
    if not text:
        return []

    # Prefer paragraph-aware packing
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: List[str] = []
    buf = ""

    def flush(buf_: str):
        if buf_:
            chunks.append(buf_)

    for p in paragraphs:
        if not buf:
            buf = p
        elif len(buf) + 2 + len(p) <= chunk_size:
            buf = buf + "\n\n" + p
        else:
            flush(buf)
            # start next with overlap tail from previous
            if chunk_overlap > 0 and len(p) > chunk_overlap:
                # keep tail from the end of previous chunk
                tail = buf[-chunk_overlap:]
                buf = (tail + "\n\n" + p)[:chunk_size]
            else:
                buf = p[:chunk_size]

        # If buffer grew too big (very long paragraph), force split
        while len(buf) > chunk_size:
            chunks.append(buf[:chunk_size])
            tail = buf[chunk_size - chunk_overlap : chunk_size] if chunk_overlap else ""
            buf = (tail + buf[chunk_size:])[:chunk_size]

    flush(buf)
    return chunks

# --------- Embeddings ---------
def embed_batches(
    client: OpenAI,
    model: str,
    texts: List[str],
    batch_size: int,
) -> List[List[float]]:
    vecs: List[List[float]] = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        # OpenAI API (python-openai >= 1.0 style)
        resp = client.embeddings.create(model=model, input=batch)
        vecs.extend([d.embedding for d in resp.data])
    return vecs

# --------- Chroma helpers ---------
def get_collection(client: PersistentClient, name: str):
    try:
        return client.get_collection(name)
    except Exception:
        return client.create_collection(name)


def sha_id(parts: List[str]) -> str:
    m = hashlib.sha256()
    for p in parts:
        m.update(p.encode("utf-8"))
        m.update(b"|")
    return m.hexdigest()

# --------- Main ingest ---------
def ingest(config: IngestConfig) -> None:
    if config.reset and config.persist_dir.exists():
        print(f"[INFO] Resetting vectorstore at {config.persist_dir}")
        shutil.rmtree(config.persist_dir, ignore_errors=True)

    config.persist_dir.mkdir(parents=True, exist_ok=True)

    # Init clients
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        print("[ERROR] OPENAI_API_KEY is not set. See .env.example", file=sys.stderr)
        sys.exit(1)

    oai = OpenAI(api_key=openai_key)
    vdb = chromadb.PersistentClient(path=str(config.persist_dir))
    col = get_collection(vdb, config.collection)

    all_docs: List[str] = []
    all_ids: List[str] = []
    all_meta: List[Dict[str, str]] = []

    files = list(iter_files(config.source_dir, config.exts))
    if not files:
        print(f"[WARN] No files with extensions {config.exts} found in {config.source_dir}")
        return

    print(f"[INFO] Found {len(files)} files. Chunking…")
    for f in files:
        raw = read_text_file(f)
        if not raw.strip():
            continue

        chunks = chunk_text(raw, config.chunk_size, config.chunk_overlap)
        if not chunks:
            continue

        base_id = sha_id([str(f.resolve()), str(len(raw))])
        for idx, ch in enumerate(chunks):
            cid = sha_id([base_id, str(idx), str(len(ch))])
            all_docs.append(ch)
            all_ids.append(cid)
            all_meta.append(
                {
                    "source_path": str(f),
                    "chunk_index": str(idx),
                    "ext": f.suffix.lower(),
                    "collection": config.collection,
                }
            )

    if not all_docs:
        print("[WARN] No chunks to index.")
        return

    print(f"[INFO] Total chunks: {len(all_docs)}. Embedding with {config.embedding_model}…")
    vectors = embed_batches(oai, config.embedding_model, all_docs, config.batch_size)

    print(f"[INFO] Upserting into Chroma at {config.persist_dir} (collection: {config.collection})…")
    # Chroma can ingest with precomputed embeddings to avoid server-side models
    col.add(documents=all_docs, embeddings=vectors, ids=all_ids, metadatas=all_meta)

    print("[OK] Ingest complete.")
    print(f"  Files:    {len(files)}")
    print(f"  Chunks:   {len(all_docs)}")
    print(f"  Store:    {config.persist_dir}")
    print(f"  Coll.:    {config.collection}")


# --------- CLI ---------
def parse_args() -> IngestConfig:
    ap = argparse.ArgumentParser(description="Build Prosody KB index → Chroma vectorstore")
    ap.add_argument(
        "--source",
        type=str,
        default="kb/prosody_corpus",
        help="Path to corpus folder with .txt/.md",
    )
    ap.add_argument(
        "--persist",
        type=str,
        default="vectorstores/prosody",
        help="Path to persistent Chroma directory",
    )
    ap.add_argument(
        "--collection",
        type=str,
        default="prosody",
        help="Chroma collection name",
    )
    ap.add_argument(
        "--model",
        type=str,
        default="text-embedding-3-small",
        help="OpenAI embedding model id",
    )
    ap.add_argument(
        "--chunk-size",
        type=int,
        default=800,
        help="Target chunk size (chars)",
    )
    ap.add_argument(
        "--chunk-overlap",
        type=int,
        default=120,
        help="Overlap size (chars)",
    )
    ap.add_argument(
        "--batch-size",
        type=int,
        default=64,
        help="Embedding batch size",
    )
    ap.add_argument(
        "--exts",
        type=str,
        default=".txt,.md",
        help="Comma-separated list of file extensions to ingest",
    )
    ap.add_argument(
        "--reset",
        action="store_true",
        help="Delete the existing persist dir before building",
    )
    args = ap.parse_args()

    return IngestConfig(
        source_dir=Path(args.source).resolve(),
        persist_dir=Path(args.persist).resolve(),
        collection=args.collection,
        embedding_model=args.model,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
        batch_size=args.batch_size,
        exts=tuple(e.strip().lower() for e in args.exts.split(",") if e.strip()),
        reset=bool(args.reset),
    )

if __name__ == "__main__":
    cfg = parse_args()
    print(
        f"[RUN] source={cfg.source_dir} → persist={cfg.persist_dir} "
        f"(collection={cfg.collection}, model={cfg.embedding_model})"
    )
    ingest(cfg)
