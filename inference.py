import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel, PeftConfig
import time

# === GLOBALS ===
PEFT_MODEL_PATH = "./lora-song4jane"
DEVICE = "cpu"

# Load LoRA config
config = PeftConfig.from_pretrained(PEFT_MODEL_PATH)

# Load base model and tokenizer
base_model = AutoModelForCausalLM.from_pretrained(
    config.base_model_name_or_path,
    torch_dtype=torch.float32,
    device_map=None
)
tokenizer = AutoTokenizer.from_pretrained(config.base_model_name_or_path)
tokenizer.pad_token = tokenizer.eos_token

# Load LoRA model
lora_model = PeftModel.from_pretrained(base_model, PEFT_MODEL_PATH)
lora_model.eval()

print(f"✅ Loaded base: {config.base_model_name_or_path} + LoRA: {PEFT_MODEL_PATH}")

def generate_text(model, prompt, tokenizer, max_new_tokens=128, temperature=0.7):
    input_text = f"<s>{prompt}</s>\n"
    inputs = tokenizer(input_text, return_tensors="pt").to(DEVICE)

    with torch.no_grad():
        output_ids = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            top_k=50,
            top_p=0.95,
            temperature=temperature,
            eos_token_id=tokenizer.eos_token_id,
            pad_token_id=tokenizer.pad_token_id,
        )
    decoded = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    return decoded[len(prompt):].strip()

def generate_base(prompt: str) -> str:
    start = time.time()
    output = generate_text(base_model, prompt, tokenizer)
    print(f"⏱️ Inference time: {time.time() - start:.2f}s")
    
    return output

def generate_lora(prompt: str) -> str:
    start = time.time()
    output = generate_text(lora_model, prompt, tokenizer)
    print(f"⏱️ Inference time: {time.time() - start:.2f}s")
    
    return output


if __name__ == "__main__":
    prompt = "Write a folk-style about church, bell and maid."
    
    print("\n🎤 Base Model Output:")
    print("---------------------")
    print(generate_base(prompt))

    print("\n🎤 LoRA Model Output:")
    print("---------------------")
    print(generate_lora(prompt))
