from __future__ import annotations

import json
import os
import uuid
from typing import Any, Dict, List, Optional

from jane.schemas import TraceEvent, TraceId, UserId
from .backends.base import VectorBackend
from .indexing import Indexer, EmbeddingsProvider, SentenceTransformersProvider
from .retrieval import Retriever


class MemoryStore:
    """
    Responsibilities:
    - Append structured trace events to an append-only JSONL log.
    - Provide simple retrieval APIs for recent history per user and per trace.
    - Bridge to vector backends (MongoDB/Chroma/Milvus) via Indexer/Retriever.
    - Keep storage concerns decoupled from business logic in engines/router.
    """

    def __init__(
        self,
        jsonl_path: str,
        vector_backend: Optional[VectorBackend] = None,
        embeddings: Optional[EmbeddingsProvider] = None,
    ) -> None:
        self.jsonl_path = jsonl_path
        os.makedirs(os.path.dirname(jsonl_path) or ".", exist_ok=True)
        self.vector_backend = vector_backend
        self.embeddings = embeddings or SentenceTransformersProvider()
        self._indexer = Indexer(backend=vector_backend, embeddings=self.embeddings) if vector_backend else None
        self._retriever = Retriever(backend=vector_backend, embeddings=self.embeddings) if vector_backend else None

    # ----------------- JSONL trace log -----------------

    def append_event(self, event: TraceEvent) -> TraceId:
        """Append one event; create a trace id if needed; return trace id."""
        trace_id = event.trace_id or TraceId(str(uuid.uuid4()))
        obj = event.model_dump()
        obj["trace_id"] = str(trace_id)
        with open(self.jsonl_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")
        return trace_id

    def get_trace(self, trace_id: TraceId) -> List[TraceEvent]:
        """Return ordered events for a given trace id (scans JSONL)."""
        out: List[TraceEvent] = []
        if not os.path.exists(self.jsonl_path):
            return out
        with open(self.jsonl_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    obj = json.loads(line)
                except Exception:
                    continue
                if obj.get("trace_id") == str(trace_id):
                    out.append(TraceEvent(**obj))
        return out

    def recent_for_user(self, user_id: UserId, limit: int = 50) -> List[TraceEvent]:
        """Return N most recent events for a user (simple tail-scan)."""
        if not os.path.exists(self.jsonl_path):
            return []
        with open(self.jsonl_path, "r", encoding="utf-8") as f:
            lines = [ln for ln in f if ln.strip()]
        events: List[TraceEvent] = []
        for line in reversed(lines):
            try:
                obj = json.loads(line)
            except Exception:
                continue
            if obj.get("user_id") == str(user_id):
                events.append(TraceEvent(**obj))
                if len(events) >= limit:
                    break
        return list(reversed(events))

    # ----------------- Vector bridge -----------------

    def upsert_vectors(self, items: List[Dict[str, Any]]) -> None:
        """
        Compute vectors for the items' 'text' and upsert into the configured vector backend.
        Item schema: { id: str, text: str, meta: dict }
        """
        if not self._indexer:
            raise RuntimeError("No vector backend configured for indexing.")
        self._indexer.upsert_texts(items)

    def search_vectors(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Embed a query and perform a vector search via the configured backend."""
        if not self._retriever:
            raise RuntimeError("No vector backend configured for retrieval.")
        return self._retriever.search(query, top_k=top_k)
