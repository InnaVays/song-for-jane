import os
from dotenv import load_dotenv
load_dotenv()


from app.graph import build_graph


if __name__ == "__main__":
    graph = build_graph()

    config = {"configurable": {"thread_id": "demo-thread-001"}}

    state = {
    "hitl": True,
    "brief": {"raw_user_message": "Rock ballad about a night train, wet asphalt, and choosing to leave."},
    "preference_profile": {
    "rhyme": {"ABAB": 0.6},
    "meter": {"iamb_4": 0.4},
    "persona": {"frontman": 0.7},
    "taboo": ["сердце разбито"],
    },
    }

    result = graph.invoke(state, config=config)

    print("=== Keys ===", list(result.keys()))
    print("=== Visible stanza (if any) ===", result.get("visible_stanza"))
    print("=== Final text (if finished) ===", result.get("final_text", "<in progress>"))