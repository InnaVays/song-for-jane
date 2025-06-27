import json
import time
from datetime import datetime
from pathlib import Path
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel, PeftConfig

def load_models_and_tokenizer(peft_model_path: str):
    config = PeftConfig.from_pretrained(peft_model_path)
    base_model = AutoModelForCausalLM.from_pretrained(config.base_model_name_or_path, torch_dtype=torch.float32)
    tokenizer = AutoTokenizer.from_pretrained(config.base_model_name_or_path)
    tokenizer.pad_token = tokenizer.eos_token

    lora_model = PeftModel.from_pretrained(base_model, peft_model_path)
    lora_model.eval()

    print(f"✅ Loaded base: {config.base_model_name_or_path} + LoRA: {peft_model_path}")
    return base_model, lora_model, tokenizer

def log_output(log_path, model_type, prompt, output, duration):
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "model": model_type,
        "prompt": prompt,
        "output": output,
        "duration_sec": round(duration, 2)
    }
    log_path = Path(log_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        
def generate_text(model, prompt, tokenizer, device, max_tokens, temperature):
    input_text = f"<s>{prompt}</s>\n"
    inputs = tokenizer(input_text, return_tensors="pt").to(device)

    with torch.no_grad():
        output_ids = model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            do_sample=True,
            top_k=50,
            top_p=0.95,
            temperature=temperature,
            eos_token_id=tokenizer.eos_token_id,
            pad_token_id=tokenizer.pad_token_id,
        )
    decoded = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    return decoded[len(prompt):].strip()

def generate_response(model_type: str, model, prompt: str, tokenizer, device: str, max_tokens: int, temperature: float, log_path: str, to_log=False) -> str:
    start = time.time()
    output = generate_text(model, prompt, tokenizer, device, max_tokens, temperature)
    duration = time.time() - start
    if to_log:
        log_output(log_path, model_type, prompt, output, duration)
    print(f"⏱️  {model_type.upper()} model time: {duration:.2f}s")
    return output

if __name__ == "__main__":
    prompt = "Write a folk-style about church, bell and maid."
    peft_model_path = "model_checkpoints/lora-song4jane"
    device = "cpu"
    log_path = "data/inference_log.jsonl"
    max_tokens = 128
    temperature = 0.7

    base_model, lora_model, tokenizer = load_models_and_tokenizer(peft_model_path, device)

    print("\n✅ Base Model Output:")
    print("---------------------")
    print(generate_response("base", base_model, prompt, tokenizer, device, max_tokens, temperature, log_path))

    print("\n✅ LoRA Model Output:")
    print("---------------------")
    print(generate_response("lora", lora_model, prompt, tokenizer, device, max_tokens, temperature, log_path))

