from typing import Optional
from jane.schemas import ChatRequest, ChatResponse, IntentLabel
from jane.classify.intent import IntentClassifier
from jane.brainstorm.engine import BrainstormEngine
from jane.edit.engine import RewriteEngine
from jane.research.engine import ResearchEngine
from jane.other.engine import OtherEngine
from jane.memory.store import MemoryStore

class Router:
    """
    High-level supervisor/dispatcher for Jane.

    Responsibilities:
    - Accept ChatRequest from API.
    - Auto-classify intent (brainstorm | rewrite | research | other).
    - Dispatch to the corresponding module engine.
    - Persist minimal trace info via MemoryStore (input/output/intent).
    - Optionally nudge the user when stuck in 'other'.
    """

    def __init__(
        self,
        classifier: IntentClassifier,
        brainstorm: BrainstormEngine,
        rewrite: RewriteEngine,
        research: ResearchEngine,
        other: OtherEngine,
        memory: MemoryStore,
    ) -> None:
        """Wire dependencies and keep no global state beyond injected components."""
        self.classifier = classifier
        self.brainstorm = brainstorm
        self.rewrite = rewrite
        self.research = research
        self.other = other
        self.memory = memory

    def route(self, req: ChatRequest) -> ChatResponse:
        """Classify the request, call the right engine, assemble ChatResponse."""
        raise NotImplementedError

    def _nudge_if_needed(self, intent: IntentLabel, recent_other_count: int) -> Optional[str]:
        """
        Produce a gentle nudge text if the user is repeatedly classified as 'other'.
        Return None if no nudge is needed.
        """
        raise NotImplementedError