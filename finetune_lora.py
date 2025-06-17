import torch
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer, DataCollatorForLanguageModeling
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from transformers import BitsAndBytesConfig

MODEL_NAME = "microsoft/phi-2" 

# Load tokenizer & model
bnb_config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.float16)
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, use_fast=True)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, quantization_config=bnb_config, device_map="auto")

# Prepare model for LoRA
model = prepare_model_for_kbit_training(model)

lora_config = LoraConfig(
    r=8,
    lora_alpha=16,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)

model = get_peft_model(model, lora_config)

# Load dataset
dataset = load_dataset("json", data_files={"train": "data/train.jsonl", "validation": "data/val.jsonl"})

# Preprocess
def tokenize(example):
    prompt = f"{example['instruction']}\nInput: {example['input']}\nOutput:"
    output = f"{example['output']}"
    full_prompt = prompt + " " + output
    return tokenizer(full_prompt, truncation=True, padding="max_length", max_length=512)

tokenized = dataset.map(tokenize, batched=True)

# Training setup
args = TrainingArguments(
    output_dir="models/song-for-jane",
    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,
    gradient_accumulation_steps=4,
    logging_steps=20,
    save_strategy="epoch",
    num_train_epochs=3,
    learning_rate=2e-4,
    bf16=True,
    evaluation_strategy="epoch",
    report_to="none"
)

trainer = Trainer(
    model=model,
    args=args,
    train_dataset=tokenized["train"],
    eval_dataset=tokenized["validation"],
    tokenizer=tokenizer,
    data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False)
)

trainer.train()

# Save LoRA adapter
model.save_pretrained("models/song-for-jane-lora")
tokenizer.save_pretrained("models/song-for-jane-lora")
