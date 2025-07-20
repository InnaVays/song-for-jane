import types
import pytest

from jane.classify.intent import IntentClassifier


class _FakeLLMResponse:
    """Mimics OpenAI chat.completions.create() response structure."""
    def __init__(self, content: str) -> None:
        self.choices = [types.SimpleNamespace(message=types.SimpleNamespace(content=content))]


class _FakeLLMClient:
    """Deterministic fake LLM; returns pre-configured label for each input text."""
    def __init__(self, mapping):
        self._mapping = mapping

    class chat:
        class completions:
            @staticmethod
            def create(*args, **kwargs):
                raise RuntimeError("This should be monkeypatched per test case.")

    # We expose the same attribute path the classifier uses:
    @property
    def chat(self):
        return types.SimpleNamespace(completions=types.SimpleNamespace(create=self._create))

    def _create(self, *, messages, model, temperature, max_tokens):
        # Extract the last user message content
        user_msg = next((m["content"] for m in messages if m["role"] == "user"), "")
        # Exact match; return configured label or 'other'
        label = self._mapping.get(user_msg, "other")
        return _FakeLLMResponse(label)


@pytest.fixture
def classifier():
    # Instantiate with a dummy model; we'll patch the client immediately
    clf = IntentClassifier(model="dummy-model", api_key="dummy")
    return clf


def test_brainstorm_basic(classifier, monkeypatch):
    """Critical: idea request should map to 'brainstorm'."""
    fake = _FakeLLMClient({"give me 5 fresh angles for a post about AI hiring": "brainstorm"})
    monkeypatch.setattr(classifier, "client", fake, raising=True)

    label = classifier.classify("give me 5 fresh angles for a post about AI hiring")
    assert label == "brainstorm"


def test_rewrite_with_paragraph(classifier, monkeypatch):
    """Critical: explicit rewrite request with a draft."""
    input_text = "please rewrite the paragraph below in my tone:\nI believe AI helps writers focus on structure."
    fake = _FakeLLMClient({input_text: "rewrite"})
    monkeypatch.setattr(classifier, "client", fake, raising=True)

    label = classifier.classify(input_text)
    assert label == "rewrite"


def test_research_factfinding(classifier, monkeypatch):
    """Critical: fact-finding / sources requested → 'research'."""
    input_text = "compare LlamaIndex vs LangChain for RAG and cite 3 sources"
    fake = _FakeLLMClient({input_text: "research"})
    monkeypatch.setattr(classifier, "client", fake, raising=True)

    label = classifier.classify(input_text)
    assert label == "research"


def test_other_greeting(classifier, monkeypatch):
    """Critical: greetings / small talk → 'other'."""
    input_text = "hi there!"
    fake = _FakeLLMClient({input_text: "other"})
    monkeypatch.setattr(classifier, "client", fake, raising=True)

    label = classifier.classify(input_text)
    assert label == "other"


def test_non_english_ru_brainstorm(classifier, monkeypatch):
    """RU input: requests ideas in Russian → 'brainstorm'."""
    input_text = "нужны идеи для статьи о личном ИИ-ассистенте"
    fake = _FakeLLMClient({input_text: "brainstorm"})
    monkeypatch.setattr(classifier, "client", fake, raising=True)

    label = classifier.classify(input_text)
    assert label == "brainstorm"


def test_non_english_ru_rewrite(classifier, monkeypatch):
    """RU input: explicit rewrite in Russian → 'rewrite'."""
    input_text = "перепиши этот абзац в моём стиле: Jane умеет думать как я и помнить мои правки."
    fake = _FakeLLMClient({input_text: "rewrite"})
    monkeypatch.setattr(classifier, "client", fake, raising=True)

    label = classifier.classify(input_text)
    assert label == "rewrite"


def test_ambiguous_long_ramble_defaults_other(classifier, monkeypatch):
    """Ambiguous/rambling content should still return a valid label; fake returns 'other'."""
    input_text = "well idk maybe ideas or sources or just rewrite everything idk lol"
    fake = _FakeLLMClient({input_text: "other"})
    monkeypatch.setattr(classifier, "client", fake, raising=True)

    label = classifier.classify(input_text)
    assert label == "other"


def test_model_drift_non_whitelisted_maps_to_other(classifier, monkeypatch):
    """If model returns unexpected token, classifier must coerce to 'other'."""
    input_text = "please help me with something"
    # Simulate a bad model output like 'IDEAS' or 'brain storm'
    fake = _FakeLLMClient({input_text: "IDEAS"})
    monkeypatch.setattr(classifier, "client", fake, raising=True)

    label = classifier.classify(input_text)
    assert label == "other"


def test_empty_text_safe_default(classifier, monkeypatch):
    """Empty input should be safely handled as 'other'."""
    input_text = ""
    fake = _FakeLLMClient({input_text: "other"})
    monkeypatch.setattr(classifier, "client", fake, raising=True)

    label = classifier.classify(input_text)
    assert label == "other"
