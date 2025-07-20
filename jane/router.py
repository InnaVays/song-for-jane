from __future__ import annotations

from typing import Optional
from time import time

from jane.schemas import ChatRequest, ChatResponse, IntentLabel, TraceEvent, TraceId
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

    Notes on frameworks (kept in mind for integration):
    - CrewAI / LangGraph can replace this imperative router with a graph/controller.
    - LangChain/LlamaIndex can be used inside engines and classifier.
    - Telemetry (OpenTelemetry) hooks can be added in try/finally blocks.
    """

    NU DGE_THRESHOLD = 1  # number of consecutive 'other' before suggesting a mode

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
        """
        Classify the request, call the right engine, assemble ChatResponse.

        The method is intentionally simple and linear for demo clarity.
        Later we can replace this with a LangGraph/CrewAI supervisor.
        """
        ts = time()

        # 1) Log input
        trace_id: TraceId = self.memory.append_event(
            TraceEvent(
                trace_id=TraceId(f"{req.user_id}:{int(ts)}"),
                user_id=req.user_id,
                ts=ts,
                type="input",
                payload={"message": req.message, "meta": req.meta or {}},
            )
        )

        # 2) Classify intent
        intent: IntentLabel = self.classifier.classify(req.message)

        self.memory.append_event(
            TraceEvent(
                trace_id=trace_id,
                user_id=req.user_id,
                ts=time(),
                type="intent",
                payload={"intent": intent},
            )
        )

        # 3) Dispatch to module
        if intent == "brainstorm":
            # (Optionally) pull context from memory here if needed
            ideas = self.brainstorm.generate(req, context=None)
            answer_text = _format_brainstorm_answer(ideas)

        elif intent == "rewrite":
            # (Optionally) pull style context via vector retrieval
            v1, v2 = self.rewrite.rewrite(req.message, style_context=None)
            answer_text = _format_rewrite_answer(v1, v2)

        elif intent == "research":
            bullets, sources = self.research.research(req.message)
            answer_text = _format_research_answer(bullets, sources)

        else:  # "other"
            answer_text = self.other.reply(req.message)
            # add a gentle nudge if user seems stuck in 'other'
            nudge = self._nudge_if_needed(intent, self._recent_other_count(req))
            if nudge:
                answer_text = f"{answer_text}\n\n{nudge}"

        # 4) Log output
        self.memory.append_event(
            TraceEvent(
                trace_id=trace_id,
                user_id=req.user_id,
                ts=time(),
                type="output",
                payload={"answer": answer_text},
            )
        )

        return ChatResponse(answer=answer_text, intent=intent, trace_id=trace_id)

    # ------------------------- internals -------------------------

    def _nudge_if_needed(self, intent: IntentLabel, recent_other_count: int) -> Optional[str]:
        """
        Produce a gentle nudge text if the user is repeatedly classified as 'other'.
        Return None if no nudge is needed.
        """
        if intent != "other":
            return None
        if recent_other_count + 1 < self.NUDGE_THRESHOLD:
            return None
        return (
            "By the way—want me to turn this into an idea, rewrite it in your style, "
            "or pull a quick research summary?"
        )

    def _recent_other_count(self, req: ChatRequest, window: int = 20) -> int:
        """
        Count how many of the recent events for this user landed in 'other'.
        This is a lightweight heuristic; a telemetry store could do this better.
        """
        count = 0
        for ev in reversed(self.memory.recent_for_user(req.user_id, limit=window)):
            if ev.type == "intent" and ev.payload.get("intent") == "other":
                count += 1
            elif ev.type == "intent":
                break
        return count


# ------------------------- formatting helpers -------------------------

def _format_brainstorm_answer(ideas) -> str:
    """Convert a list[BrainstormIdea] into a compact text block."""
    lines = []
    for i, idea in enumerate(ideas, start=1):
        lines.append(f"{i}. {idea.title} — {idea.summary}")
        if getattr(idea, "angle", None):
            lines.append(f"   ↳ angle: {idea.angle}")
        if getattr(idea, "rationale", None):
            lines.append(f"   ↳ why: {idea.rationale}")
    return "\n".join(lines) if lines else "No ideas generated."

def _format_rewrite_answer(v1: str, v2: str) -> str:
    """Present two rewrite variants with distinct intents."""
    return (
        "Variant A (strict style):\n"
        f"{v1}\n\n"
        "Variant B (style + clarity):\n"
        f"{v2}"
    )

def _format_research_answer(bullets, sources) -> str:
    """Render research bullets and attach concise sources metadata."""
    bl = "\n".join(f"- {b}" for b in bullets) if bullets else "- No findings."
    src = "\n".join(
        f"[{i+1}] {s.get('title','source')} — {s.get('url','')}"
        for i, s in enumerate(sources[:5])
    ) or "[no sources]"
    return f"{bl}\n\nSources:\n{src}"
