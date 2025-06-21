from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments, DataCollatorForLanguageModeling
from peft import LoraConfig, get_peft_model, TaskType
from datasets import load_dataset
import torch
from transformers import EarlyStoppingCallback

import time

# Use a small base model for CPU training
model_id = "microsoft/phi-1_5"
dataset_path = "data/love_lyrics__prompts.json"

print("✅ Loading base model on CPU...")
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.float32,       # Use float32 for CPU
)

tokenizer = AutoTokenizer.from_pretrained(model_id)
tokenizer.pad_token = tokenizer.eos_token 

print("✅ Applying LoRA...")
lora_config = LoraConfig(
    r=4,
    lora_alpha=16,
    target_modules=["q_proj", "v_proj"],  
    lora_dropout=0.1,
    bias="none",
    task_type=TaskType.CAUSAL_LM,
)

model = get_peft_model(model, lora_config)

print("✅ Loading dataset...")
dataset = load_dataset("json", data_files=dataset_path, split="train[:]")

def tokenize_function(example):
    text = f"<s>{example['prompt']}</s>\n{example['response']}"
    return tokenizer(text, padding="max_length", truncation=True, max_length=128) # 128 to fit in small RAM

start_time = time.time()

tokenized_dataset = dataset.map(tokenize_function, remove_columns=dataset.column_names)

print("✅ Configuring Trainer...")
training_args = TrainingArguments(
    dataloader_pin_memory=False,
    output_dir="./lora-output",
    num_train_epochs=3,
    per_device_train_batch_size=1,  
    gradient_accumulation_steps=1,
    logging_dir="./logs",
    logging_steps=10,
    save_strategy="epoch",
    learning_rate=3e-4,
    warmup_steps=10,
    fp16=False,
    bf16=False,
    report_to="none",
    metric_for_best_model="loss",      
    greater_is_better=False,           
)

print("✅ Building trainer on CPU...")
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
    tokenizer=tokenizer,
    data_collator=DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False),
)

print("✅ Starting training on CPU...")
trainer.train()

end_time = time.time()
inference_time = end_time - start_time
print( f"\n Inference time: {inference_time:.2f} seconds" )

print("✅ Saving model...")
model.save_pretrained("./lora-song4jane")
tokenizer.save_pretrained("./lora-song4jane")

print("✅ Training complete.")