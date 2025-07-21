import types
import pytest

from jane.rewrite.engine import RewriteEngine
from jane.rewrite.style_fewshot import StyleRetriever


class _FakeLLM:
    """Minimal LangChain-compatible fake: has .invoke(payload) -> str"""
    def __init__(self, reply: str) -> None:
        self._reply = reply

    def invoke(self, _payload):
        return self._reply


class _FakeRetriever(StyleRetriever):
    """Return deterministic style examples regardless of query."""
    def __init__(self):
        super().__init__(vector_search_callable=lambda query, top_k=3: [])
        self._examples = [
            {"id": "a1", "text": "I write with short punchy sentences. Humor allowed.", "score": 0.9, "meta": {}},
            {"id": "a2", "text": "I like parallel structure and rhythm in lists.", "score": 0.8, "meta": {}},
        ]

    def get_style_examples(self, query: str, top_k: int = 3):
        return self._examples[:top_k]


@pytest.fixture
def engine(monkeypatch):
    eng = RewriteEngine(provider="openai", model="dummy", temperature_style=0.0, temperature_improve=0.0)

    # Bypass real LLMs
    def _ensure_llms_stub():
        eng._llm_style = _FakeLLM("STYLE_OUTPUT")
        eng._llm_improve = _FakeLLM("IMPROVED_OUTPUT")
    monkeypatch.setattr(eng, "_ensure_llms", _ensure_llms_stub, raising=True)

    return eng


def test_rewrite_returns_two_variants(engine):
    """Engine should return (v1_style_mine, v2_style_improved) as non-empty strings."""
    v1, v2 = engine.rewrite("Draft text to rewrite.", style_context="keep it concise")
    assert isinstance(v1, str) and v1.strip()
    assert isinstance(v2, str) and v2.strip()
    assert v1 == "STYLE_OUTPUT"
    assert v2 == "IMPROVED_OUTPUT"


def test_rewrite_uses_retriever_when_attached(engine, monkeypatch):
    """When a retriever is attached, engine should call it for examples."""
    retr = _FakeRetriever()
    engine.attach_retriever(retr)

    called = {"flag": False}
    def spy_get_examples(query: str, top_k: int = 3):
        called["flag"] = True
        return retr._examples[:top_k]

    monkeypatch.setattr(retr, "get_style_examples", spy_get_examples, raising=True)

    v1, v2 = engine.rewrite("A longish draft that should trigger retrieval.", style_context="")
    assert called["flag"] is True
    assert v1 and v2  # both variants produced


def test_lorafy_is_noop_returns_none(engine):
    """LoRA hook is a no-op placeholder; should return None for now."""
    out = engine.lorafy({"sample": "text"})
    assert out is None
