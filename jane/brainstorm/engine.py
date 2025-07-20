from typing import Any, List, Optional
from jane.schemas import ChatRequest, BrainstormIdea

class BrainstormEngine:
    """
    Idea generation engine.

    Responsibilities:
    - Generate 2–3 distinct concepts for a topic (e.g., 'my style', 'unexpected', 'structural').
    - Support multiple creative modes (e.g., 'multipersona_cot', 'triz').
    - Optionally consume style/context retrieved from MemoryStore.
    - Remain stateless across calls (state lives in MemoryStore).
    """

    def __init__(
        self,
        mode: str = "multipersona_cot",
        provider: str = "openai",  # fireworks | together | anthropic | openai
        **provider_kwargs: Any
    ) -> None:
        """Store configuration, prompt templates, and provider credentials."""
        self.mode = mode
        self.provider = provider
        self.provider_kwargs = provider_kwargs

    def generate(self, req: ChatRequest, context: Optional[str] = None) -> List[BrainstormIdea]:
        """
        Produce a small set of structured ideas for the request.
        `context` may include retrieved style snippets or prior notes.
        """
        raise NotImplementedError

    def supported_modes(self) -> List[str]:
        """Return a list of supported creative modes."""
        return ["multipersona_cot", "triz"]
