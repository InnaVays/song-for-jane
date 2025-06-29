import json
import uuid

MEMORY_FILE = "user_memory_log.json"

def save_feedback(prompt, output, feedback=None, keep=True, persona=None):
    record = {
        "id": str(uuid.uuid4()),
        "prompt": prompt,
        "output": output,
        "keep": keep,
        "feedback": feedback,
        "persona": persona
    }
    try:
        with open(MEMORY_FILE, 'a') as f:
            f.write(json.dumps(record) + "\n")
    except Exception as e:
        print("Error saving memory:", e)


def load_past_memories(n=10, only_kept=True):
    memories = []
    try:
        with open("user_memory_log.json", 'r') as f:
            for line in f:
                record = json.loads(line)
                if only_kept and not record["keep"]:
                    continue
                memories.append(record)
    except FileNotFoundError:
        return []
    return memories[-n:]