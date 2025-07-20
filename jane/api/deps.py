from __future__ import annotations

from jane.router import Router
from jane.classify.intent import IntentClassifier
from jane.brainstorm.engine import BrainstormEngine
from jane.rewrite.engine import RewriteEngine
from jane.research.engine import ResearchEngine
from jane.other.engine import OtherEngine
from jane.memory.store import MemoryStore


def build_router() -> Router:
    """
    Dependency factory for wiring a default Router instance.

    Notes:
    - In production, replace engines with LangChain/LlamaIndex-backed implementations.
    - MemoryStore can be pointed at MongoDB/Chroma via config.
    """
    classifier = IntentClassifier()
    brainstorm = BrainstormEngine(mode="multipersona_cot", provider="openai")
    rewrite = RewriteEngine(provider="openai")
    research = ResearchEngine()
    other = OtherEngine()

    memory = MemoryStore(
        jsonl_path="data/user_memory_log.jsonl",
        vector_backend=None,  # 'mongo' | 'chroma' when enabled
    )

    return Router(
        classifier=classifier,
        brainstorm=brainstorm,
        rewrite=rewrite,
        research=research,
        other=other,
        memory=memory,
    )
