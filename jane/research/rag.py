from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from langchain.schema import Document
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser


@dataclass
class RagResult:
    """Normalized result of a RAG query over local memory."""
    bullets: List[str]
    sources: List[Dict[str, Any]]


class MemoryRetrieverAdapter:
    """
    Adapter that converts MemoryStore.search_vectors() results into LangChain Documents.

    Expected search result item:
      { "id": str, "text": str, "score": float, "meta": dict }
    """

    def __init__(self, vector_search_callable) -> None:
        self._search = vector_search_callable

    def get_documents(self, query: str, top_k: int = 6) -> List[Document]:
        results = self._search(query=query, top_k=top_k)
        docs: List[Document] = []
        for r in results:
            docs.append(
                Document(
                    page_content=r.get("text", ""),
                    metadata={
                        "id": r.get("id"),
                        "score": float(r.get("score", 0.0)),
                        **(r.get("meta", {}) or {}),
                    },
                )
            )
        return docs


class RagPipeline:
    """
    Minimal LangChain RetrievalQA-style pipeline over MemoryStore.

    This avoids tying directly to a specific vector DB by using MemoryRetrieverAdapter.
    """

    def __init__(
        self,
        retriever: MemoryRetrieverAdapter,
        provider: str = "openai",          # openai | anthropic | fireworks | together
        model: str = "gpt-4o-mini",
        temperature: float = 0.1,
        **provider_kwargs: Any
    ) -> None:
        self.retriever = retriever
        self.provider = provider
        self.model = model
        self.temperature = temperature
        self.provider_kwargs = provider_kwargs
        self._llm = None

    def ask(self, query: str, top_k: int = 6) -> RagResult:
        """
        Retrieve docs from memory, summarize into bullets, and expose normalized sources.
        """
        from langchain.prompts import PromptTemplate
        from langchain_core.runnables import RunnablePassthrough
        from langchain.schema.output_parser import StrOutputParser

        self._ensure_llm()

        docs = self.retriever.get_documents(query, top_k=top_k)
        context = "
ы