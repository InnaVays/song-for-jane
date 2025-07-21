from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

from jane.rewrite.style_fewshot import build_fewshot_prompt, StyleRetriever
from jane.rewrite import lora_hook


class RewriteEngine:
    """
    Personalized rewrite engine (LangChain).

    Responsibilities:
    - Retrieve user's style exemplars from MemoryStore (vector search).
    - Construct few-shot prompts with style guidance.
    - Produce two variants:
        v1_style_mine: "strict style" (minimal semantic change)
        v2_style_improved: "style + clarity/structure improvement"
    - Expose `lorafy()` to trigger (future) LoRA fine-tuning.

    Notes:
    - This engine is intentionally stateless; state lives in MemoryStore.
    - Inference provider is selected via `provider` string and kwargs.
    """

    def __init__(
        self,
        provider: str = "openai",  # fireworks | together | anthropic | openai
        model: str = "gpt-4o-mini",
        temperature_style: float = 0.2,
        temperature_improve: float = 0.3,
        **provider_kwargs: Any
    ) -> None:
        self.provider = provider
        self.model = model
        self.temperature_style = temperature_style
        self.temperature_improve = temperature_improve
        self.provider_kwargs = provider_kwargs
        self._retriever: Optional[StyleRetriever] = None
        self._llm_style = None
        self._llm_improve = None

    # -------- public API --------

    def attach_retriever(self, retriever: StyleRetriever) -> None:
        """
        Attach a StyleRetriever that knows how to query MemoryStore's vector backend.
        """
        self._retriever = retriever

    def rewrite(self, draft: str, style_context: Optional[str] = None) -> Tuple[str, str]:
        """
        Return two variants: (v1_style_mine, v2_style_improved).

        - Uses MemoryStore-driven few-shot examples (if retriever is attached).
        - Falls back to zero-shot if no examples are available.
        """
        from langchain.prompts import PromptTemplate
        from langchain_core.output_parsers import StrOutputParser

        # Initialize LLMs lazily to avoid hard deps in constructor
        self._ensure_llms()

        # 1) Build few-shot prompt (examples from MemoryStore, if available)
        examples = []
        if self._retriever:
            examples = self._retriever.get_style_examples(query=draft, top_k=3)

        fs_prompt_style, fs_prompt_improve = build_fewshot_prompt(
            draft=draft,
            style_context=style_context or "",
            examples=examples,
        )

        # 2) Format prompts for two chains
        # Variant A: strict style (minimal editing)
        tmpl_style = PromptTemplate.from_template(fs_prompt_style)
        chain_style = tmpl_style | self._llm_style | StrOutputParser()
        v1_style = chain_style.invoke({})

        # Variant B: style + clarity/structure
        tmpl_improve = PromptTemplate.from_template(fs_prompt_improve)
        chain_improve = tmpl_improve | self._llm_improve | StrOutputParser()
        v2_improved = chain_improve.invoke({})

        return v1_style.strip(), v2_improved.strip()

    def lorafy(self, texts: Dict[str, str]) -> Optional[str]:
        """
        Delegate to the LoRA training hook (PEFT/Unsloth). Returns adapter version id or None.
        """
        return lora_hook.lorafy(texts=texts)

    # -------- internals --------

    def _ensure_llms(self) -> None:
        """
        Lazy-create LangChain chat models for both variants based on `provider`.
        """
        if self._llm_style is not None and self._llm_improve is not None:
            return

        # Keep imports local to avoid hard dependency unless used
        if self.provider == "openai":
            from langchain_openai import ChatOpenAI
            self._llm_style = ChatOpenAI(model=self.model, temperature=self.temperature_style, **self.provider_kwargs)
            self._llm_improve = ChatOpenAI(model=self.model, temperature=self.temperature_improve, **self.provider_kwargs)

        elif self.provider == "anthropic":
            from langchain_anthropic import ChatAnthropic
            self._llm_style = ChatAnthropic(model=self.model, temperature=self.temperature_style, **self.provider_kwargs)
            self._llm_improve = ChatAnthropic(model=self.model, temperature=self.temperature_improve, **self.provider_kwargs)

        elif self.provider == "fireworks":
            from langchain_fireworks import ChatFireworks
            self._llm_style = ChatFireworks(model=self.model, temperature=self.temperature_style, **self.provider_kwargs)
            self._llm_improve = ChatFireworks(model=self.model, temperature=self.temperature_improve, **self.provider_kwargs)

        elif self.provider == "together":
            from langchain_together import ChatTogether
            self._llm_style = ChatTogether(model=self.model, temperature=self.temperature_style, **self.provider_kwargs)
            self._llm_improve = ChatTogether(model=self.model, temperature=self.temperature_improve, **self.provider_kwargs)

        else:
            raise ValueError(f"Unknown provider: {self.provider}")
