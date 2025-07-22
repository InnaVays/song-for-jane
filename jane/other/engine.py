from __future__ import annotations

import re
from typing import Optional


class OtherEngine:
    """
    Lightweight small-talk / free-form engine.

    Responsibilities:
    - Provide a short, clear chat response for off-topic or open-ended inputs.
    - Gently nudge the user toward one of Jane's core modes:
        • brainstorm  — idea generation
        • rewrite     — personal-style rewriting
        • research    — fact gathering with sources
    - Keep zero external dependencies; simple, deterministic behavior.

    Notes:
    - Router may add an additional nudge if the user repeatedly lands in 'other'.
      This engine still includes its own gentle one-liner to guide the next step.
    """

    def __init__(self, enable_smart_nudges: bool = True) -> None:
        """
        Args:
            enable_smart_nudges: when True, infer the most relevant next action
                                 from lightweight keyword cues; otherwise show a generic triad nudge.
        """
        self.enable_smart_nudges = enable_smart_nudges

    # ----------------- public API -----------------

    def reply(self, message: str) -> str:
        """
        Produce a short, helpful response and append a single gentle nudge.

        The heuristic is intentionally simple:
          - If we detect keywords hinting ideas → suggest 'brainstorm'.
          - If we detect 'rewrite/edit/tone' patterns → suggest 'rewrite'.
          - If we detect 'sources/facts/compare' patterns → suggest 'research'.
          - Otherwise → show a neutral triad of choices.

        Returns:
            A concise chat reply ending with exactly one nudge sentence.
        """
        base = self._base_reply(message)
        nudge = self._smart_nudge(message) if self.enable_smart_nudges else self._generic_nudge()
        return f"{base}\n\n{nudge}"

    # ----------------- internals -----------------

    def _base_reply(self, message: str) -> str:
        """
        Keep a neutral, friendly tone. Reflect the user's message briefly without over-indexing on style.
        """
        msg = (message or "").strip()
        if not msg:
            return "Got it. What would you like to work on first?"
        # Light reflection capped in length to avoid echoing long inputs.
        preview = (msg[:160] + "…") if len(msg) > 160 else msg
        return f"I hear you. We can take this further.\nYou said: “{preview}”"

    def _smart_nudge(self, message: str) -> str:
        """
        Pick one specific next step when possible; else fall back to generic nudge.
        """
        affinity = self._detect_affinity(message or "")
        if affinity == "brainstorm":
            return "Want me to turn this into 2–3 fresh angles? Say “brainstorm” or just drop a topic."
        if affinity == "rewrite":
            return "Want me to rewrite this in your voice? Say “rewrite” and paste the draft."
        if affinity == "research":
            return "Want a quick factual summary with sources? Say “research” and add your question."
        return self._generic_nudge()

    def _generic_nudge(self) -> str:
        """
        Neutral triad nudge — short and skimmable.
        """
        return (
            "Next step: **brainstorm** (ideas), **rewrite** (your style), or **research** (facts + sources)?"
        )

    def _detect_affinity(self, text: str) -> Optional[str]:
        """
        Extremely lightweight keyword cues; language-agnostic where possible.

        Returns:
            'brainstorm' | 'rewrite' | 'research' | None
        """
        t = text.lower()

        # brainstorm cues
        if _any(
            t,
            [
                r"\bbrainstorm\b",
                r"\bideas?\b",
                r"\bangles?\b",
                r"\bconcepts?\b",
                r"\bcreative\b",
                r"\bhook(s)?\b",
            ],
        ):
            return "brainstorm"

        # rewrite cues
        if _any(
            t,
            [
                r"\brewrite\b",
                r"\bedit\b",
                r"\bpolish\b",
                r"\bclean\s*up\b",
                r"\btone\b",
                r"\bvoice\b",
                r"\bstyle\b",
                r"\brephrase\b",
            ],
        ):
            return "rewrite"

        # research cues
        if _any(
            t,
            [
                r"\bresearch\b",
                r"\bsources?\b",
                r"\bcite\b",
                r"\bfacts?\b",
                r"\bcompare\b",
                r"\bversus\b|\bvs\.\b|\bvs\b",
                r"\bevidence\b",
                r"\bstatistics?\b",
            ],
        ):
            return "research"

        return None


# ----------------- helpers -----------------

def _any(text: str, patterns: list[str]) -> bool:
    return any(re.search(p, text) for p in patterns)
