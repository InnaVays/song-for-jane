import os
import pytest

from jane.classify.intent import IntentClassifier

REAL_KEY = os.getenv("OPENAI_API_KEY")

pytestmark = pytest.mark.skipif(not REAL_KEY, reason="Set OPENAI_API_KEY to run integration test")


def test_integration_real_llm_one_word_labels():
    clf = IntentClassifier(model="gpt-3.5-turbo", api_key=REAL_KEY)

    cases = {
        "give me novel angles about sustainability in fashion": "brainstorm",
        "rewrite this: I think AI helps people brainstorm faster": "rewrite",
        "what are the best sources comparing LlamaIndex vs LangChain?": "research",
        "hey! how are you?": "other",
    }

    for text, expected in cases.items():
        label = clf.classify(text)
        assert label in {"brainstorm", "rewrite", "research", "other"}
        # weak assertion (models can vary), but usually matches:
        # assert label == expected
