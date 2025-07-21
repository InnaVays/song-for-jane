from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, Iterable, List, Optional, Sequence


class VectorBackend(ABC):
    """
    Common interface for vector backends used by Jane's memory layer.
    Backends are intentionally dumb: they accept pre-computed vectors and upsert/search.

    Item schema for upsert:
      { "id": str, "text": str, "meta": dict, "vector": List[float] }

    Result schema for search() return:
      { "id": str, "text": str, "score": float, "meta": dict }
    """

    @abstractmethod
    def upsert(self, items: Sequence[Dict[str, Any]]) -> None:
        """Insert or update items with pre-computed vectors."""
        raise NotImplementedError

    @abstractmethod
    def search(self, query_vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """Return top_k nearest items with scores and metadata."""
        raise NotImplementedError

    @abstractmethod
    def ensure_index(self, **kwargs: Any) -> None:
        """Create or verify the vector index configuration."""
        raise NotImplementedError
