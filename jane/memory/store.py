from typing import Any, Dict, List, Optional
from jane.schemas import TraceEvent, TraceId, UserId

class MemoryStore:
    """
    Central memory abstraction for Jane.

    Responsibilities:
    - Append structured trace events to an append-only log (jsonl or similar).
    - Provide simple retrieval APIs for recent history per user.
    - Bridge to vector backends (MongoDB/Chroma/etc) via indexing/retrieval helpers.
    - Keep storage concerns decoupled from business logic in engines/router.
    """

    def __init__(
        self,
        jsonl_path: str,
        vector_backend: Optional[str] = None,  # 'mongo' | 'chroma' | None
        **backend_kwargs: Any
    ) -> None:
    
        """Configure local log path and optional vector backend settings."""
        self.jsonl_path = jsonl_path
        self.vector_backend = vector_backend
        self.backend_kwargs = backend_kwargs

    def append_event(self, event: TraceEvent) -> TraceId:
        """Append one event and return its trace id (or reuse existing id)."""
        raise NotImplementedError

    def get_trace(self, trace_id: TraceId) -> List[TraceEvent]:
        """Return ordered events for a given trace id."""
        raise NotImplementedError

    def recent_for_user(self, user_id: UserId, limit: int = 50) -> List[TraceEvent]:
        """Return the N most recent events for a user."""
        raise NotImplementedError

    def upsert_vectors(self, items: List[Dict[str, Any]]) -> None:
        """
        Upsert embedding records into the vector backend.
        Item schema recommendation: { 'id': str, 'text': str, 'meta': dict }.
        """
        raise NotImplementedError

    def search_vectors(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve nearest records from the vector backend.
        Return a list of { 'id': str, 'text': str, 'score': float, 'meta': dict }.
        """
        raise NotImplementedError
