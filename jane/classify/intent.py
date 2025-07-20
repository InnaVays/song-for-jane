from __future__ import annotations
import logging
from typing import Literal

from jane.schemas import IntentLabel

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None  # allow repo to install later

logger = logging.getLogger(__name__)


class IntentClassifier:
    """
    LLM-powered intent classifier.

    Contract:
    - Input: raw user text.
    - Output: one of {brainstorm, rewrite, research, other}.
    - Uses a cheap LLM model (e.g., gpt-3.5-turbo).
    - Prompt is strict: "Output only one word. Nothing else!"
    """

    def __init__(self, model: str = "gpt-3.5-turbo", api_key: str | None = None) -> None:
        if OpenAI is None:
            raise RuntimeError("openai package not installed. Install with `pip install openai`.")
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def classify(self, text: str) -> IntentLabel:
        """Send a strict classification prompt to the LLM and parse one-word answer."""
        system_prompt = (
            "You are a strict classifier. "
            "Read the user input and respond with exactly one word only:\n"
            "- brainstorm → if the text asks for ideas, variations, creativity, brainstorming.\n"
            "- rewrite → if the text provides a draft or paragraph to improve, rewrite, adapt.\n"
            "- research → if the text asks for facts, sources, explanations, comparisons.\n"
            "- other → for greetings, chit-chat, or anything not covered.\n\n"
            "Output only one word: 'brainstorm', 'rewrite', 'research', 'other'. Nothing else."
        )

        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text},
                ],
                temperature=0.0,
                max_tokens=2,
            )
            label_raw = resp.choices[0].message.content.strip().lower()
        except Exception as e:
            logger.error(f"LLM classify error: {e}")
            return "other"

        if label_raw not in {"brainstorm", "rewrite", "research", "other"}:
            return "other"

        return label_raw  # type: ignore[return-value]

