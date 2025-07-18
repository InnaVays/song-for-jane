import yaml
import json
import time
from pathlib import Path
from src.scrape.gutenberg_scraper import scrape_gutenberg_sources
from src.scrape.prompt_writer import create_prompts_from_stanzas
from src.train.lora_train_CPU import train_lora_cpu
from src.inference.inference_utils import load_models_and_tokenizer, generate_response
from src.evaluate_outputs import evaluate_text_metrics
from src.utils.files import load_json, load_jsonl, save_jsonl
import warnings
warnings.filterwarnings("ignore", message=".*BLEU score evaluates to 0.*")

# Load config
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)


# === 1. Scrape from Gutenberg ===
print("✅ Scraping Gutenberg sources...")
scrape_gutenberg_sources(
    source_list=config["scrape"]["source_list"],
    output_file=config["scrape"]["output_file"],
)

# === 2. Create Prompt-Output pairs ===
print("✅ Creating prompts from stanzas...")
create_prompts_from_stanzas(
    input_file=config["prompt"]["input_file"],
    output_file=config["prompt"]["output_file"],
)

# === 3. Train LoRA on CPU ===
print("✅ Training LoRA model on CPU...")
train_lora_cpu(
    dataset_file=config["train"]["dataset_file"],
    output_dir=config["train"]["output_dir"],
    base_model=config["train"]["base_model"],
    num_epochs=config["train"]["num_epochs"],
    batch_size=config["train"]["batch_size"],
    gradient_accumulation=config["train"]["gradient_accumulation"],
    learning_rate=config["train"]["learning_rate"]
)

# === 4. Run Inference (Base vs LoRA) ===
print("✅ Running inference on test prompts...")

test_prompts = load_json(config["inference"]["test_prompts"])
log_path = config["inference"]["save_outputs_to"]
peft_model_path = config["train"]["output_dir"]
device = config["inference"]["device"]
max_tokens = config["inference"]["max_new_tokens"]
temperature = config["inference"]["temperature"]

# Load models only once
base_model, lora_model, tokenizer = load_models_and_tokenizer(peft_model_path)

outputs = []
for sample in test_prompts:
    prompt = sample["prompt"]
    base_output = generate_response("base", base_model, prompt, tokenizer, device, max_tokens, temperature, log_path)
    lora_output = generate_response("lora", lora_model, prompt, tokenizer, device, max_tokens, temperature, log_path)

    outputs.append({
        "prompt": prompt,
        "base_output": base_output,
        "lora_output": lora_output
    })

save_jsonl(outputs, config["inference"]["save_outputs_to"])

# === 5. Evaluation ===
print("✅ Evaluating outputs...")
outputs = load_jsonl(config["inference"]["save_outputs_to"])
for o in outputs:
    print("\nPrompt:", o["prompt"])
    print("\nScore Base Model response:")
    scores = evaluate_text_metrics(o["prompt"], o["base_output"])
    for k, v in scores.items():
        print(f"{k}: {v:.4f}")

    print("\nScore LoRa Model response:")
    scores = evaluate_text_metrics(o["prompt"], o["lora_output"])
    for k, v in scores.items():
        print(f"{k}: {v:.4f}")

print("\n✅ Demo pipeline complete!")
