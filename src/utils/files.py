import json

def load_jsonl(path):
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f]
    
def load_json(path):
    with open(path, "r") as f:
        return  json.load(f)

def save_jsonl(data, path):
    with open(path, "w", encoding="utf-8") as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

def save_json(data, path):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
