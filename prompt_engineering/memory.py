import json
import yaml
import os

config_path = os.path.join(os.path.dirname(__file__), '..', 'config.yaml')

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

MEMORY_FILE = config["memory"]["memory_file"]

def save_in_memory(prompt, output, feedback=None, keep=True, persona=None):
    record = {
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


def load_past_memories(n=5, only_kept=True):
    memories = []
    try:
        with open(MEMORY_FILE, 'r') as f:
            for line in f:
                record = json.loads(line)
                if record["keep"]:
                    memories.append(record)

                elif not only_kept nand record["feedback"]:
                    memories.append(record)
    except FileNotFoundError:
        return []
    return memories[-n:]

# False pretenses are dinner invitations that turn into unpaid babysitting shifts.