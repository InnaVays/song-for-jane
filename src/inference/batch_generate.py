from src.inference.inference_utils import generate_base, generate_lora
from src.utils.files import load_jsonl, save_jsonl

prompts = load_jsonl("data/prompts.jsonl")

base_outputs, lora_outputs = [], []

for ex in prompts:
    prompt = ex["prompt"]
    base_outputs.append({"prompt": prompt, "output": generate_base(prompt)})
    lora_outputs.append({"prompt": prompt, "output": generate_lora(prompt)})

save_jsonl(base_outputs, "data/results_base.jsonl")
save_jsonl(lora_outputs, "data/results_lora.jsonl")