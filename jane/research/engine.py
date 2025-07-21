from __future__ import annotations

from typing import Any, Dict, List, Tuple

from jane.research.rag import RagPipeline, RagResult
from jane.research.web_tools import WebSearchTool
from jane.research.ranker import Ranker


class ResearchEngine:
    """
    Research engine combining local RAG (history) and web search (found).

    Flow:
      1) Try RAG over local memory; if strong enough, summarize + return.
      2) If not strong, expand with web search results (Tavily/SerpAPI), summarize.
      3) Merge, rank, and annotate bullets with labels: "history" | "found".
      4) Return compact bullets + normalized sources.

    Contracts:
      - research(query) -> (bullets, sources)
      - sources: list of {title, url, score, label}
      - bullets: short, source-backed statements with inline labels when possible
    """

    def __init__(
        self,
        rag: RagPipeline,
        web: WebSearchTool,
        ranker: Ranker,
        min_history_bullets: int = 2,
        max_total_sources: int = 8,
    ) -> None:
        self.rag = rag
        self.web = web
        self.ranker = ranker
        self.min_history_bullets = min_history_bullets
        self.max_total_sources = max_total_sources

    def research(self, query: str) -> Tuple[List[str], List[Dict[str, Any]]]:
        """
        Execute research over memory + web and return (bullets, sources).
        """
        # 1) RAG over local memory
        hist: RagResult = self.rag.ask(query)

        bullets: List[str] = []
        sources: List[Dict[str, Any]] = []

        if hist.bullets:
            for b in hist.bullets:
                bullets.append(f"{b} [history]")
        for s in hist.sources:
            s = dict(s)
            s["label"] = "history"
            sources.append(s)

        # 2) If not enough, augment with web search
        if len(bullets) < self.min_history_bullets:
            found_results = self.web.search_and_summarize(query, max_results=6)
            for b in found_results["bullets"]:
                bullets.append(f"{b} [found]")
            for s in found_results["sources"]:
                s = dict(s)
                s["label"] = "found"
                sources.append(s)

        # 3) Rank & trim sources; lightly re-order bullets by source ranks
        ranked_sources = self.ranker.rank_sources(sources)[: sel]()
