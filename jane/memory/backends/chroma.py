from __future__ import annotations
from typing import Any, Dict, List, Sequence

from .base import VectorBackend

try:
    import chromadb
    from chromadb.config import Settings
except ImportError:  # pragma: no cover
    chromadb = None
    Settings = None


class ChromaVectorBackend(VectorBackend):
    """
    Local Chroma backend (persistent or in-memory).

    - We provide vectors explicitly; no embedding_function is required.
    - Persistence is optional via `persist_directory`.
    """

    def __init__(
        self,
        collection: str = "jane_memory",
        persist_directory: str | None = ".chroma",
    ) -> None:
        if chromadb is None:
            raise RuntimeError("chromadb is not installed. `pip install chromadb`.")
        if persist_directory:
            client = chromadb.PersistentClient(path=persist_directory, settings=Settings())
        else:
            client = chromadb.Client(Settings())

        self.collection = client.get_or_create_collection(name=collection)

    def upsert(self, items: Sequence[Dict[str, Any]]) -> None:
        ids = [it["id"] for it in items]
        docs = [it.get("text", "") for it in items]
        metas = [it.get("meta", {}) for it in items]
        vecs = [it["vector"] for it in items]
        # Chroma upsert via add() with explicit embeddings
        self.collection.upsert(ids=ids, documents=docs, metadatas=metas, embeddings=vecs)

    def search(self, query_vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        res = self.collection.query(query_embeddings=[query_vector], n_results=max(1, top_k))
        # Chroma returns batched lists; unwrap first batch
        out = []
        if not res or not res.get("ids"):
            return out
        for i in range(len(res["ids"][0])):
            out.append(
                {
                    "id": res["ids"][0][i],
                    "text": res["documents"][0][i] if res.get("documents") else "",
                    "score": float(res["distances"][0][i]) if res.get("distances") else 0.0,
                    "meta": res["metadatas"][0][i] if res.get("metadatas") else {},
                }
            )
        return out

    def ensure_index(self, **kwargs: Any) -> None:
        # Chroma collections are ready-to-query; no extra index creation required.
        return None
