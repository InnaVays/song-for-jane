import os
from dotenv import load_dotenv
load_dotenv()


from app.graph import build_graph

from pathlib import Path
import subprocess, sys

def ensure_vectorstores():
    kb_dir = Path("vectorstores/prosody")
    mem_dir = Path("vectorstores/memory")

    # Если папка пуста/нет коллекции — собираем
    if not kb_dir.exists() or not any(kb_dir.iterdir()):
        print("[INIT] Building Prosody KB index...")
        subprocess.check_call([sys.executable, "app/indexing/build_kb_index.py",
                               "--source", "kb/prosody_corpus",
                               "--persist", "vectorstores/prosody",
                               "--collection", "prosody"])

    if not mem_dir.exists() or not any(mem_dir.iterdir()):
        print("[INIT] Building User Memory index...")
        subprocess.check_call([sys.executable, "app/indexing/build_memory_index.py",
                               "--memory", "memory",
                               "--persist", "vectorstores/memory",
                               "--collection", "memory"])

if __name__ == "__main__":
    ensure_vectorstores()
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