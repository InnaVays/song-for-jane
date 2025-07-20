from jane.schemas import IntentLabel

class IntentClassifier:
    """
    Zero/low-shot intent classifier.

    Contract:
    - Pure function style: do not mutate internal state.
    - Return one of: 'brainstorm', 'rewrite', 'research', 'other'.
    - May combine rules + LLM decisioning behind the scenes (later).
    """

    def __init__(self) -> None:
        """Initialize prompt templates, rules, or downstream clients if needed."""
        ...

    def classify(self, text: str) -> IntentLabel:
        """Map raw text to one intent label."""
        raise NotImplementedError
