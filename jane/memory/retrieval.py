from __future__ import annotations
from typing import Any, Dict, List

from .backends.base import VectorBackend
from .indexing import EmbeddingsProvider


class Retriever:
    """
    Retrieval helper: embed a query and ask the backend for nearest items.
    """

    def __init__(self, backend: VectorBackend, embeddings: EmbeddingsProvider) -> None:
        self.backend = backend
        self.embeddings = embeddings

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        qv = self.embeddings.embed_query(query)
        return self.backend.search(qv, top_k=top_k)
