from __future__ import annotations
from typing import Any, Dict, Iterable, List, Sequence

from .backends.base import VectorBackend


class EmbeddingsProvider:
    """
    Simple provider interface; swap out with your preferred library.
    """

    def embed_texts(self, texts: Sequence[str]) -> List[List[float]]:
        """Return a vector per input text."""
        raise NotImplementedError

    def embed_query(self, text: str) -> List[float]:
        """Return a single vector for a search query."""
        raise NotImplementedError


class SentenceTransformersProvider(EmbeddingsProvider):
    """
    Default local embeddings provider using sentence-transformers.

    Model: all-MiniLM-L6-v2 (384 dims) by default.
    """

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> None:
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore
        except ImportError as e:  # pragma: no cover
            raise RuntimeError("Install sentence-transformers to use SentenceTransformersProvider.") from e
        self.model = SentenceTransformer(model_name)

    def embed_texts(self, texts: Sequence[str]) -> List[List[float]]:
        return [vec.tolist() for vec in self.model.encode(list(texts), normalize_embeddings=True)]

    def embed_query(self, text: str) -> List[float]:
        return self.embed_texts([text])[0]


class Indexer:
    """
    Indexing helper: takes raw items -> computes vectors -> upserts to backend.

    Expected item input (without vectors):
      { "id": str, "text": str, "meta": dict }
    """

    def __init__(self, backend: VectorBackend, embeddings: EmbeddingsProvider) -> None:
        self.backend = backend
        self.embeddings = embeddings

    def upsert_texts(self, items: Sequence[Dict[str, Any]]) -> None:
        texts = [it.get("text", "") for it in items]
        vecs = self.embeddings.embed_texts(texts)
        payload = []
        for it, v in zip(items, vecs):
            payload.append(
                {
                    "id": it["id"],
                    "text": it.get("text", ""),
                    "meta": it.get("meta", {}),
                    "vector": v,
                }
            )
        self.backend.upsert(payload)
