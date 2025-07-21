import pytest
from typing import Any, Dict, List, Tuple

from jane.research.engine import ResearchEngine
from jane.research.rag import RagPipeline, RagResult
from jane.research.web_tools import WebSearchTool
from jane.research.ranker import Ranker


class _FakeRag(RagPipeline):
    """Fake RAG pipeline returning a predefined result; no LangChain calls."""
    def __init__(self, bullets: List[str], sources: List[Dict[str, Any]]):
        # Do not call parent __init__
        self._bullets = bullets
        self._sources = sources

    def ask(self, query: str, top_k: int = 6) -> RagResult:
        return RagResult(bullets=list(self._bullets), sources=list(self._sources))


class _FakeWeb(WebSearchTool):
    """Fake web tool; counts calls and returns canned results."""
    def __init__(self, bullets: List[str], sources: List[Dict[str, Any]]):
        # Do not call parent __init__
        self._bullets = bullets
        self._sources = sources
        self.calls = 0

    def search_and_summarize(self, query: str, max_results: int = 6) -> Dict[str, Any]:
        self.calls += 1
        return {"bullets": list(self._bullets), "sources": list(self._sources)}


class _PassThroughRanker(Ranker):
    """Ranker that returns sources as-is (deterministic, no BM25 dependency)."""
    def rank_sources(self, sources: List[Dict]) -> List[Dict]:
        return list(sources)


def test_history_sufficient_no_web_called():
    """If history yields enough bullets, engine should not call web."""
    hist_bullets = ["A from history.", "B from history.", "C from history."]
    hist_sources = [{"title": "Mem1", "url": "", "score": 0.6}, {"title": "Mem2", "url": "", "score": 0.5}]
    web_bullets = ["X from web."]
    web_sources = [{"title": "Web1", "url": "http://w1", "score": 0.9}]

    rag = _FakeRag(hist_bullets, hist_sources)
    web = _FakeWeb(web_bullets, web_sources)
    ranker = _PassThroughRanker()

    engine = ResearchEngine(rag=rag, web=web, ranker=ranker, min_history_bullets=2, max_total_sources=8)
    bullets, sources = engine.research("test query")

    # Web should not be called
    assert web.calls == 0

    # All bullets are labeled [history]
    assert all(b.endswith("[history]") for b in bullets)

    # Sources carry label 'history'
    assert all(s.get("label") == "history" for s in sources)


def test_cold_query_augments_with_web_and_labels():
    """If history is weak, engine augments with web and labels bullets/sources correctly."""
    hist_bullets = ["Only one history point."]
    hist_sources = [{"title": "Mem1", "url": "", "score": 0.2}]
    web_bullets = ["One web point.", "Another web point."]
    web_sources = [
        {"title": "Web1", "url": "http://w1", "score": 0.9},
        {"title": "Web2", "url": "http://w2", "score": 0.7},
    ]

    rag = _FakeRag(hist_bullets, hist_sources)
    web = _FakeWeb(web_bullets, web_sources)
    ranker = _PassThroughRanker()

    engine = ResearchEngine(rag=rag, web=web, ranker=ranker, min_history_bullets=2, max_total_sources=8)
    bullets, sources = engine.research("cold query")

    # Web should be called because history < min_history_bullets
    assert web.calls == 1

    # Bullets include both history and found labels
    assert any(b.endswith("[history]") for b in bullets)
    assert any(b.endswith("[found]") for b in bullets)

    # Sources are labeled appropriately
    hist_labeled = [s for s in sources if s.get("label") == "history"]
    found_labeled = [s for s in sources if s.get("label") == "found"]
    assert hist_labeled and found_labeled


def test_sources_are_trimmed_to_max_total_sources():
    """Engine should respect max_total_sources limit after ranking."""
    hist_bullets = ["H1.", "H2."]
    hist_sources = [{"title": f"Mem{i}", "url": "", "score": 0.1 * i} for i in range(1, 6)]
    web_bullets = ["W1.", "W2."]
    web_sources = [{"title": f"Web{i}", "url": f"http://w{i}", "score": 0.9 - 0.05 * i} for i in range(1, 6)]

    rag = _FakeRag(hist_bullets, hist_sources)
    web = _FakeWeb(web_bullets, web_sources)
    ranker = _PassThroughRanker()

    engine = ResearchEngine(rag=rag, web=web, ranker=ranker, min_history_bullets=3, max_total_sources=5)
    bullets, sources = engine.research("trim test")

    assert len(sources) <= 5  # trimmed
    # Labels present
    assert all(s.get("label") in {"history", "found"} for s in sources)
