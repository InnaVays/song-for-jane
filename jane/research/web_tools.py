from __future__ import annotations

from typing import Any, Dict, List

from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser


class WebSearchTool:
    """
    Web search + summarize wrapper.

    Two backends supported via LangChain:
      - Tavily (recommended for research)
      - SerpAPI (fallback)

    API keys are taken from environment variables expected by LangChain libs:
      - TAVILY_API_KEY
      - SERPAPI_API_KEY
    """

    def __init__(
        self,
        provider: str = "tavily",      # 'tavily' | 'serpapi'
        llm_provider: str = "openai",  # used for summarization step
        llm_model: str = "gpt-4o-mini",
        llm_temperature: float = 0.2,
        **llm_kwargs: Any
    ) -> None:
        self.provider = provider
        self.llm_provider = llm_provider
        self.llm_model = llm_model
        self.llm_temperature = llm_temperature
        self.llm_kwargs = llm_kwargs

        self._search = None
        self._llm = None

    # ----------------- public -----------------

    def search_and_summarize(self, query: str, max_results: int = 6) -> Dict[str, Any]:
        """
        Run a web search, keep top N, summarize into compact bullets.
        """
        self._ensure_clients()

        # 1) raw search results (title/url/snippet)
        results = self._search(query, k=max_results)
        sources = []
        for r in results[:max_results]:
            # normalize shape across providers
            title = r.get("title") or r.get("source") or "Source"
            url = r.get("url") or r.get("link") or ""
            snippet = r.get("content") or r.get("snippet") or ""
            score = float(r.get("score", 0.0)) if isinstance(r.get("score", 0.0), (int, float)) else 0.0
            sources.append({"title": title, "url": url, "snippet": snippet, "score": score})

        # 2) summarize snippets to bullets
        context = "\n\n".join(f"[{i+1}] {s['title']}\n{s['snippet']}" for i, s in enumerate(sources) if s["snippet"])
        prompt = PromptTemplate.from_template(
            "You are a factual summarizer. Based ONLY on the provided web snippets, "
            "produce 3–5 short, source-backed bullets for the query.\n"
            "Do not invent content beyond the snippets.\n\n"
            "Query:\n{query}\n\n"
            "Snippets:\n{context}\n\n"
            "Output: 3–5 bullets, each a single sentence. No preface, no extras."
        )
        chain = prompt | self._llm | StrOutputParser()
        raw = chain.invoke({"query": query, "context": context})
        bullets = _split_bullets(raw)

        return {"bullets": bullets, "sources": sources}

    # ----------------- internals -----------------

    def _ensure_clients(self) -> None:
        if self._llm is None:
            if self.llm_provider == "openai":
                from langchain_openai import ChatOpenAI
                self._llm = ChatOpenAI(model=self.llm_model, temperature=self.llm_temperature, **self.llm_kwargs)
            elif self.llm_provider == "anthropic":
                from langchain_anthropic import ChatAnthropic
                self._llm = ChatAnthropic(model=self.llm_model, temperature=self.llm_temperature, **self.llm_kwargs)
            elif self.llm_provider == "fireworks":
                from langchain_fireworks import ChatFireworks
                self._llm = ChatFireworks(model=self.llm_model, temperature=self.llm_temperature, **self.llm_kwargs)
            elif self.llm_provider == "together":
                from langchain_together import ChatTogether
                self._llm = ChatTogether(model=self.llm_model, temperature=self.llm_temperature, **self.llm_kwargs)
            else:
                raise ValueError(f"Unknown llm_provider: {self.llm_provider}")

        if self._search is None:
            if self.provider == "tavily":
                # langchain_community.tools.tavily_search might change; use a stable utility where possible
                from langchain_community.tools.tavily_search import TavilySearchResults
                tool = TavilySearchResults(max_results=10)
                self._search = lambda q, k=6: tool.invoke({"query": q})[:k]  # returns list of dicts
            elif self.provider == "serpapi":
                from langchain_community.utilities import SerpAPIWrapper
                serp = SerpAPIWrapper()
                self._search = lambda q, k=6: serp.results(q)["organic_results"][:k]
            else:
                raise ValueError(f"Unknown provider: {self.provider}")


def _split_bullets(text: str) -> List[str]:
    raw_lines = [ln.strip("-• \t") for ln in text.splitlines() if ln.strip()]
    out: List[str] = []
    for ln in raw_lines:
        if not ln:
            continue
        out.append(ln.rstrip(".") + ".")
    return out[:5]
