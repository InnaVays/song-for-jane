from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments, DataCollatorForLanguageModeling
from peft import LoraConfig, get_peft_model, TaskType
from datasets import load_dataset
import torch
import time

def train_lora_cpu(
    dataset_file: str,
    output_dir: str,
    base_model: str,
    num_epochs: int = 3,
    batch_size: int = 1,
    gradient_accumulation: int = 1,
    learning_rate: float = 3e-4
):
    print("✅ Loading base model on CPU...")
    model = AutoModelForCausalLM.from_pretrained(
        base_model,
        torch_dtype=torch.float32,
    )

    tokenizer = AutoTokenizer.from_pretrained(base_model)
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
    dataset = load_dataset("json", data_files=dataset_file, split="train[:]")

    def tokenize_function(example):
        text = f"<s>{example['prompt']}</s>\n{example['response']}"
        return tokenizer(text, padding="max_length", truncation=True, max_length=128) # ON CPU

    tokenized_dataset = dataset.map(tokenize_function, remove_columns=dataset.column_names)

    print("✅ Configuring Trainer...")
    training_args = TrainingArguments(
        dataloader_pin_memory=False,
        output_dir=output_dir,
        num_train_epochs=num_epochs,
        per_device_train_batch_size=batch_size,
        gradient_accumulation_steps=gradient_accumulation,
        logging_dir="./logs",
        logging_steps=10,
        save_strategy="epoch",
        learning_rate=learning_rate,
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
    start_time = time.time()
    trainer.train()
    end_time = time.time()

    print(f"\n⏱️ Training time: {end_time - start_time:.2f} seconds")

    print("✅ Saving model...")
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)

    print("✅ Training complete.")

def main():
        pass

if __name__ == "__main__":
    main()
