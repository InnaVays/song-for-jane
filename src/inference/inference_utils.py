import json
import time
from datetime import datetime
from pathlib import Path
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel, PeftConfig

from src.utils.config_loader import load_config

cfg = load_config()
LOG_PATH = Path(cfg["logging"]["log_path"])
PEFT_MODEL_PATH = cfg["model"]["lora_path"]
DEVICE = cfg["model"]["device"]


print("✅ Loading models and tokenizer...")
config = PeftConfig.from_pretrained(PEFT_MODEL_PATH)
base_model = AutoModelForCausalLM.from_pretrained(config.base_model_name_or_path, torch_dtype=torch.float32)
tokenizer = AutoTokenizer.from_pretrained(config.base_model_name_or_path)
tokenizer.pad_token = tokenizer.eos_token

lora_model = PeftModel.from_pretrained(base_model, PEFT_MODEL_PATH)
lora_model.eval()

print(f"✅ Loaded base: {config.base_model_name_or_path} + LoRA: {PEFT_MODEL_PATH}")

def generate_text(model, prompt):
    input_text = f"<s>{prompt}</s>\n"
    inputs = tokenizer(input_text, return_tensors="pt").to(DEVICE)

    with torch.no_grad():
        output_ids = model.generate(
            **inputs,
            max_new_tokens=MAX_TOKENS,
            do_sample=True,
            top_k=50,
            top_p=0.95,
            temperature=TEMPERATURE,
            eos_token_id=tokenizer.eos_token_id,
            pad_token_id=tokenizer.pad_token_id,
        )
    decoded = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    return decoded[len(prompt):].strip()


def log_output(model_type, prompt, output, duration):
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "model": model_type,
        "prompt": prompt,
        "output": output,
        "duration_sec": round(duration, 2)
    }
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def generate_base(prompt: str) -> str:
    start = time.time()
    output = generate_text(base_model, prompt)
    duration = time.time() - start
    log_output("base", prompt, output, duration)
    print(f"✅  Base model time: {duration:.2f}s")
    return output


def generate_lora(prompt: str) -> str:
    start = time.time()
    output = generate_text(lora_model, prompt)
    duration = time.time() - start
    log_output("lora", prompt, output, duration)
    print(f"✅  LoRA model time: {duration:.2f}s")
    return output

if __name__ == "__main__":
    prompt = "Write a folk-style about church, bell and maid."
    
    print("\n✅ Base Model Output:")
    print("---------------------")
    print(generate_base(prompt))

    print("\n✅ LoRA Model Output:")
    print("---------------------")
    print(generate_lora(prompt))
