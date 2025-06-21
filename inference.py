import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel, PeftConfig
import time 

# Define your prompt
user_prompt = "Write a folk-style about church, bell and maid."
input_text = f"<s>{user_prompt}</s>\n"

# Load the config
peft_model_path = "./lora-song4jane"

# Loading PEFT config...
config = PeftConfig.from_pretrained(peft_model_path)

print(f"✅ Base model: {config.base_model_name_or_path}")
base_model = AutoModelForCausalLM.from_pretrained(
    config.base_model_name_or_path,
    torch_dtype=torch.float32,
)

# Loading tokenizer...
tokenizer = AutoTokenizer.from_pretrained(config.base_model_name_or_path)
tokenizer.pad_token = tokenizer.eos_token
inputs = tokenizer(input_text, return_tensors="pt")

# === INFERENCE: BASE MODEL ===
print("🎤 Generating with BASE model...")
start_time = time.time()
with torch.no_grad():
    base_output = base_model.generate(
        **inputs,
        max_new_tokens=128,
        do_sample=True,
        top_k=50,
        top_p=0.95,
        temperature=0.7,
        eos_token_id=tokenizer.eos_token_id,
        pad_token_id=tokenizer.pad_token_id,
    )
base_time = time.time() - start_time

lora_model = PeftModel.from_pretrained(base_model, peft_model_path)
lora_model.eval()

start_time = time.time()

# === INFERENCE: LoRa MODEL ===
print("🎤 Generating with LoRa model...")
with torch.no_grad():
    lora_output = lora_model.generate(
        **inputs,
        max_new_tokens=128,
        do_sample=True,
        top_k=50,
        top_p=0.95,
        temperature=0.7,
        eos_token_id=tokenizer.eos_token_id,
        pad_token_id=tokenizer.pad_token_id,
    )

lora_time = time.time() - start_time

print("\n🧾 Prompt:")
print(user_prompt)

print("\n🧠 Base Model Output:")
print("---------------------")
print(tokenizer.decode(base_output[0], skip_special_tokens=True)[len(user_prompt):].strip())
print(f"⏱️ Inference time: {base_time:.2f} seconds")

print("\n✨ LoRA Model Output:")
print("---------------------")
print(tokenizer.decode(lora_output[0], skip_special_tokens=True)[len(user_prompt):].strip())
print(f"⏱️ Inference time: {lora_time:.2f} seconds")
