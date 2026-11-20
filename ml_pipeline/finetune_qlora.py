"""QLoRA fine-tuning starter for a Hugging Face causal language model.

Install ml dependencies and run: python ml_pipeline/finetune_qlora.py
"""

import argparse
import json


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="meta-llama/Llama-3.2-3B-Instruct")
    parser.add_argument("--dataset", default="ml_pipeline/train_dataset.jsonl")
    parser.add_argument("--output", default="ml_pipeline/qlora-output")
    args = parser.parse_args()

    import torch
    from datasets import load_dataset
    from peft import LoraConfig, get_peft_model
    from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments
    from trl import SFTTrainer

    tokenizer = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForCausalLM.from_pretrained(
        args.model,
        device_map="auto",
        torch_dtype=torch.bfloat16,
        load_in_4bit=True,
    )
    model = get_peft_model(
        model,
        LoraConfig(r=16, lora_alpha=32, lora_dropout=0.05, task_type="CAUSAL_LM"),
    )
    dataset = load_dataset("json", data_files=args.dataset, split="train")

    def format_example(example: dict) -> str:
        target = json.dumps(example["expected_json"], separators=(",", ":"))
        return f"### Query:\n{example['prompt']}\n\n### JSON:\n{target}"

    trainer = SFTTrainer(
        model=model,
        train_dataset=dataset,
        formatting_func=format_example,
        tokenizer=tokenizer,
        args=TrainingArguments(
            output_dir=args.output,
            per_device_train_batch_size=2,
            gradient_accumulation_steps=4,
            learning_rate=2e-4,
            num_train_epochs=3,
            bf16=True,
            logging_steps=10,
            save_strategy="epoch",
        ),
    )
    trainer.train()
    trainer.save_model(args.output)
    tokenizer.save_pretrained(args.output)


if __name__ == "__main__":
    main()
