from __future__ import annotations
from typing import Any, Dict
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from app.state import AppState
from app.nodes.brief import brief_node
from app.nodes.planner import planner_node
from app.nodes.selector import selector_node
from app.nodes.retriever import retriever_node
from app.nodes.style_fuser import style_fuser_node
from app.nodes.triz_booster import triz_booster_node
from app.nodes.poem_writer import poem_writer_node
from app.nodes.critic import critic_node
from app.nodes.decider import decider_node
from app.nodes.feedback_interpreter import feedback_interpreter_node
from app.nodes.replanner import replanner_node
from app.nodes.versioner import versioner_node
from app.nodes.memory_io import memory_io_node


def finalize_node(state: Dict[str, Any]) -> Dict[str, Any]:
    stanzas = state.get("stanzas", [])
    final_text = "
".join(stanzas) if stanzas else ""
    return {"final_text": final_text}

def build_graph() -> Any:
    g = StateGraph(AppState)

    g.add_node("brief", brief_node)
    g.add_node("planner", planner_node)
    g.add_node("selector", selector_node)
    g.add_node("retriever", retriever_node)
    g.add_node("style_fuser", style_fuser_node)
    g.add_node("triz", triz_booster_node)
    g.add_node("poem_writer", poem_writer_node)
    g.add_node("critic", critic_node)
    g.add_node("decider", decider_node)
    g.add_node("feedback_interpreter", feedback_interpreter_node)
    g.add_node("replanner", replanner_node)
    g.add_node("versioner", versioner_node)
    g.add_node("memory_io", memory_io_node)
    g.add_node("finalize", finalize_node)
    g.set_entry_point("brief")
    g.add_edge("brief", "planner")
    g.add_edge("planner", "selector")
    g.add_edge("selector", "retriever")
    g.add_edge("retriever", "style_fuser")
    g.add_edge("style_fuser", "triz")
    g.add_edge("triz", "poem_writer")
    g.add_edge("poem_writer", "critic")
    g.add_edge("critic", "decider")

    def route_decision(state: Dict[str, Any]):
        d = state.get("last_decision", "accept")
        if d == "rewrite":
            return "replanner"
        if state.get("hitl", True):
            return "feedback_interpreter"
        return "memory_io"


    g.add_conditional_edges("decider", route_decision, {
        "replanner": "replanner",
        "feedback_interpreter": "feedback_interpreter",
        "memory_io": "memory_io",
        })

    g.add_edge("replanner", "versioner")
    g.add_edge("versioner", "selector")
    g.add_edge("feedback_interpreter", "memory_io")

    def continue_or_end(state: Dict[str, Any]):
        stanzas = state.get("stanzas", [])
        target = state.get("chosen_plan", {}).get("stanza_count", {}).get("value", 4)
        if len(stanzas) >= int(target):
            return "finalize"
        return "triz"


    g.add_conditional_edges("memory_io", continue_or_end, {"triz": "triz", "finalize": "finalize"})
    g.add_edge("finalize", END)


    checkpointer = SqliteSaver("runs/checkpoints.db")
    return g.compile(checkpointer=checkpointer)