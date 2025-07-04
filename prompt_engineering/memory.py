import json
import uuid

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

MEMORY_FILE = config["memory"]["memory_file"]

def save_in_memory(prompt, output, feedback=None, keep=True, persona=None):
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


def load_past_memories(n=5, only_kept=True, include_rejected_with_feedback=False):
    memories = []
    try:
        with open(MEMORY_FILE, 'r') as f:
            for line in f:
                record = json.loads(line)
                if only_kept and not record["keep"]:
                    if include_rejected_with_feedback and record.get("feedback"):
                        memories.append(record)
                    continue
                elif not only_kept or record["keep"]:
                    memories.append(record)
    except FileNotFoundError:
        return []
    return memories[-n:]