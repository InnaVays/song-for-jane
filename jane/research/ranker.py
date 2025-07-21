from __future__ import annotations

from typing import Dict, List


class Ranker:
    """
    Source ranker that combines BM25 (if available) and numeric score fallback.

    Strategy:
      - If 'rank_bm25' is installed and we have snippets, compute BM25 scores against the query title/url.
      - Combine BM25 with any provided 'score' field (normalized).
      - Sort descending by combined score.
      - If BM25 is unavailable, sort by 'score' descending and keep stable order otherwise.
    """

    def __init__(self) -> None:
        try:
            from rank_bm25 import BM25Okapi  # type: ignore
            self._bm25_available = True
        except Exception:
            self._bm25_available = False

    def rank_sources(self, sources: List[Dict]) -> List[Dict]:
        if not sources:
            return []

        if self._bm25_available:
            # Build a trivial corpus from title + snippet
            from rank_bm25 import BM25Okapi  # type: ignore

            corpus = []
            for s in sources:
                text = f"{s.get('title','')} {s.get('snippet','')}".strip()
                tokens = _tokenize(text)
                corpus.append(tokens)

            bm25 = BM25Okapi(corpus)
            # Query here is weak; in real impl pass the actual search query.
            # We'll approximate with top title tokens to avoid side-channel deps.
            query_tokens = _tokenize(" ".join(s.get("title", "") for s in sources[:3]))
            scores = bm25.get_scores(query_tokens)

            # Combine BM25 with provided numeric 'score' if any (scaled 0..1)
            out = []
            for s, bm in zip(sources, scores):
                base = float(s.get("score", 0.0))
                combined = _normalize(base) * 0.3 + _normalize(bm) * 0.7
                s2 = dict(s)
                s2["combined_score"] = float(combined)
                out.append(s2)

            return sorted(out, key=lambda x: x["combined_score"], reverse=True)

        # Fallback: numeric score desc, stable otherwise
        return sorted(sources, key=lambda x: float(x.get("score", 0.0)), reverse=True)


def _tokenize(text: str) -> List[str]:
    return [t.lower() for t in text.split() if t.strip()]


def _normalize(x: float) -> float:
    # Simple squashing to 0..1; adjust if you have calibrated metrics.
    if x < 0:
        return 0.0
    if x > 1e6:  # guard weird magnitudes
        return 1.0
    return x / (1.0 + x)
