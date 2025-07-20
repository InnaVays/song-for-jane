from typing import Any, Dict, List, Tuple

class ResearchEngine:
    """
    Research engine combining local RAG and web search.

    Responsibilities:
    - Query local memory first (RAG); if confidence is low, hit web tools.
    - Rank sources and annotate bullets with labels: "history" | "found".
    - Return a compact, structured summary and a source list.
    """

    def __init__(self, **tooling: Any) -> None:
        """Wire retrieval backends and web-search clients as needed."""
        self.tooling = tooling

    def research(self, query: str) -> Tuple[List[str], List[Dict[str, Any]]]:
        """
        Return (bullets, sources), where:
        - bullets: list of short statements with inline labels.
        - sources: list of {title, url, score, label}.
        """
        raise NotImplementedError
