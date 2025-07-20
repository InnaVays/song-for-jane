class OtherEngine:
    """
    Fallback small-talk / free-form engine.

    Responsibilities:
    - Provide a polite, helpful response when intent is 'other'.
    - Optionally add a gentle nudge towards brainstorm/rewrite/research.
    """

    def __init__(self) -> None:
        """Keep this engine lightweight; no heavy dependencies."""
        ...

    def reply(self, message: str) -> str:
        """Produce a short, helpful response."""
        raise NotImplementedError
