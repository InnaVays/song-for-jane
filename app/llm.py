"""Unified LLM caller with Small/Medium/Large presets.
Optionally:
MODEL_SMALL, MODEL_MEDIUM, MODEL_LARGE (fall back to sane defaults).
"""
from __future__ import annotations
from typing import Optional, Dict, Any
import os
from openai import OpenAI


class LLMRouter:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        # defaults — override via env if needed
        self.model_small = os.getenv("MODEL_SMALL", "gpt-4.1-nano")
        self.model_medium = os.getenv("MODEL_MEDIUM", "gpt-4o-mini")
        self.model_large = os.getenv("MODEL_LARGE", "gpt-4o")

    def _choose(self, tier: str) -> str:
        if tier == "small":
            return self.model_small
        if tier == "medium":
            return self.model_medium
        if tier == "large":
            return self.model_large
        
        raise ValueError(f"Unknown tier: {tier}")


    def json_call(
        self,
        tier: str,
        system: str,
        user: str,
        temperature: float = 0.2,
        max_output_tokens: int = 1024,
        ) -> str:
        """Call model with JSON response format and return raw JSON text."""
        
        model = self._choose(tier)

        resp = self.client.chat.completions.create(
            model=model,
            messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
            ],
            temperature=temperature,
            response_format={"type": "json_object"},
            max_tokens=max_output_tokens,
            )
        return resp.choices[0].message.content


    def text_call(
        self,
        tier: str,
        system: str,
        user: str,
        temperature: float = 0.6,
        max_output_tokens: int = 512,
        ) -> str:

        model = self._choose(tier)
        
        resp = self.client.chat.completions.create(
            model=model,
            messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
            ],
            temperature=temperature,
            max_tokens=max_output_tokens,
            )
        return resp.choices[0].message.content

llm = LLMRouter()

