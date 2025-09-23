from __future__ import annotations
from typing import Any, Dict
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver

from app.state import AppState
from app.nodes.bootstrap import bootstrap_node
from app.nodes.brief import brief_node
from app.nodes.context_pack import context_pack_node
from app.nodes.master_planner import master_planner_node
from app.nodes.retrieval_plans import retrieval_plans_node
from app.nodes.micro_fetch import micro_fetch_node
from app.nodes.selector_ab import selector_ab_node
from app.nodes.writer import writer_node
from app.nodes.show_to_user import show_to_user_node
from app.nodes.feedback_interpreter import feedback_interpreter_node
from app.nodes.memory_update import memory_update_node
from app.nodes.loop_controller import loop_controller_node
from app.nodes.finalize import finalize_node


def build_graph_memory_fueled() -> Any:
    g = StateGraph(AppState)
    g.add_node("brief", brief_node)
    g.add_node("context_pack", context_pack_node)
    g.add_node("master_planner", master_planner_node)
    g.add_node("retrieval_plans", retrieval_plans_node)
    g.add_node("micro_fetch", micro_fetch_node)
    g.add_node("selector_ab", selector_ab_node)
    g.add_node("writer", writer_node)
    g.add_node("show_to_user", show_to_user_node)
    g.add_node("feedback_interpreter", feedback_interpreter_node)
    g.add_node("memory_update", memory_update_node)
    g.add_node("loop_controller", loop_controller_node)
    g.add_node("finalize", finalize_node)

    g.set_entry_point("bootstrap")

    g.add_edge("bootstrap", "brief")
    g.add_edge("brief", "context_pack")
    g.add_edge("context_pack", "master_planner")

    # Per-stanza loop
    g.add_edge("master_planner", "retrieval_plans")
    g.add_edge("retrieval_plans", "micro_fetch")
    g.add_edge("micro_fetch", "selector_ab")
    g.add_edge("selector_ab", "writer")
    g.add_edge("writer", "show_to_user")

    # Pause after show_to_user until feedback arrives
    def wait_feedback(state: Dict[str, Any]):
        return "feedback_interpreter" if state.get("raw_feedback") else END

    g.add_conditional_edges("show_to_user", wait_feedback, {
    "feedback_interpreter": "feedback_interpreter",
    END: END,
    })

    g.add_edge("feedback_interpreter", "memory_update")
    g.add_edge("memory_update", "loop_controller")

    def continue_or_finalize(state: Dict[str, Any]):
        stanzas = state.get("stanzas", []) or []
        plan = state.get("plan", {})
        target = int(plan.get("stanza_count", 4))
        return "retrieval_plans" if len(stanzas) < target else "finalize"

    g.add_conditional_edges("loop_controller", continue_or_finalize, {
        "retrieval_plans": "retrieval_plans",
        "finalize": "finalize",
    })
    g.add_edge("finalize", END)

    checkpointer = SqliteSaver("runs/checkpoints.db")
    return g.compile(checkpointer=checkpointer)