from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict

from dotenv import load_dotenv

# Ensure project root on sys.path when running directly
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Import the Memory-Fueled graph
from app.graph_memory_fueled import build_graph_memory_fueled


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Run the Memory-Fueled PaE graph (Branch the context, not the plan)"
    )
    ap.add_argument(
        "--thread-id",
        type=str,
        default="mf-demo-001",
        help="Persistent conversation/session id (used by LangGraph checkpoint)",
    )
    ap.add_argument(
        "--brief",
        type=str,
        default=None,
        help="Raw user message to start a new/updated brief",
    )
    ap.add_argument(
        "--feedback",
        type=str,
        default=None,
        help="Raw feedback after show_to_user (e.g., 'A; faster tempo; add image: neon puddles')",
    )
    ap.add_argument(
        "--print-state",
        action="store_true",
        help="Print compact state summary (keys, stanza count, chosen context)",
    )
    ap.add_argument(
        "--json",
        action="store_true",
        help="Print raw JSON result (in addition to human-friendly output)",
    )
    return ap.parse_args()


def ensure_env() -> None:
    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        print("[ERROR] OPENAI_API_KEY is not set. See .env.example", file=sys.stderr)
        sys.exit(1)


def pretty_preview(result: Dict[str, Any]) -> None:
    print("\n================= RESULT =================")
    vis = result.get("visible_stanza")
    if vis:
        print(f"[Stanza #{vis.get('k','?')}]")
        print(vis.get("text", "").rstrip())
    else:
        print("(No stanza in this step)")

    if "awaiting_feedback" in result:
        print("\nAwaiting feedback:", bool(result.get("awaiting_feedback")))
        fp = result.get("feedback_prompt")
        if fp:
            print("Feedback prompt:", fp)

    final = result.get("final_text")
    if final:
        print("\n------------- FINAL TEXT -------------")
        print(final.rstrip())
        print("--------------------------------------")


def compact_state_line(result: Dict[str, Any]) -> str:
    keys = list(result.keys())
    sz = len(result.get("stanzas", []) or [])
    chosen = result.get("chosen_context")
    awaiting = result.get("awaiting_feedback")
    return f"keys={keys}; stanzas={sz}; chosen_context={chosen}; awaiting_feedback={awaiting}"


def main() -> None:
    ensure_env()

    args = parse_args()
    graph = build_graph_memory_fueled()

    # Build minimal delta state for this turn:
    # - If starting/adjusting brief: pass brief.raw_user_message
    # - If continuing with feedback: pass raw_feedback
    state_delta: Dict[str, Any] = {}

    if args.brief:
        state_delta["brief"] = {"raw_user_message": args.brief}

    if args.feedback:
        # You can put any free text here: "ACCEPT", "A", "B", "merge A&B", etc.
        state_delta["raw_feedback"] = args.feedback

    if not state_delta:
        # If nothing provided, seed a default brief (first run convenience)
        state_delta["brief"] = {
            "raw_user_message": "Write a night-train rock ballad with wet asphalt and a hard choice."
        }
        print("[INFO] No --brief or --feedback provided; using a default brief.")

    # Run the graph
    config = {"configurable": {"thread_id": args.thread_id}}
    result = graph.invoke(state_delta, config=config)

    # Human-friendly view
    pretty_preview(result)

    # Optional compact state info
    if args.print_state:
        print("\n[STATE]", compact_state_line(result))

    # Optional raw JSON
    if args.json:
        print("\n[JSON]\n", json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
