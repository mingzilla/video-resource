from unsloth import FastLanguageModel  # must be first import

import json
import logging
import os
from pathlib import Path

from datasets import Dataset
from trl import SFTConfig, SFTTrainer

from shared_utils.external.env_var.env_var_reader import EnvVarReader

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Config:
    def __init__(self):
        EnvVarReader.load_dotenv()
        self.is_prod: bool = EnvVarReader.is_prod()

        config_root = EnvVarReader.get_str('CONFIG_ROOT', 'scripts_sh/ex_001__train')
        config_file = EnvVarReader.get_str('CONFIG_FILE', 'run.json')

        with open(os.path.join(config_root, config_file)) as f:
            data = json.load(f)

        self.jsonl_path: str = data['jsonl_path']
        self.base_model: str = data['base_model']
        self.output_dir: str = data['output_dir']
        self.max_seq_length: int = data['max_seq_length']
        self.load_in_4bit: bool = data['load_in_4bit']
        self.lora_rank: int = data['lora_rank']
        self.lora_alpha: int = data['lora_alpha']
        self.num_epochs: int = data['num_epochs']
        self.per_device_train_batch_size: int = data['per_device_train_batch_size']
        self.gradient_accumulation_steps: int = data['gradient_accumulation_steps']
        self.warmup_steps: int = data['warmup_steps']
        self.learning_rate: float = data['learning_rate']
        self.weight_decay: float = data['weight_decay']


def load_dataset(jsonl_path: str) -> Dataset:
    records = []
    with open(jsonl_path) as f:
        for line in f:
            records.append(json.loads(line.strip()))
    logger.info(f"Loaded {len(records)} records from {jsonl_path}")
    return Dataset.from_list(records)


def main():
    config = Config()

    logger.info(f"Loading base model: {config.base_model}")
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=config.base_model,
        max_seq_length=config.max_seq_length,
        dtype=None,
        load_in_4bit=config.load_in_4bit,
    )

    model = FastLanguageModel.get_peft_model(
        model,
        r=config.lora_rank,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        lora_alpha=config.lora_alpha,
        lora_dropout=0,
        bias="none",
        use_gradient_checkpointing="unsloth",
        random_state=42,
    )

    dataset = load_dataset(config.jsonl_path)

    def format_messages(batch):
        return {
            "text": [
                tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)
                for messages in batch["messages"]
            ]
        }

    dataset = dataset.map(format_messages, batched=True)

    output_dir = Path(config.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset,
        args=SFTConfig(
            dataset_text_field="text",
            max_length=config.max_seq_length,
            output_dir=str(output_dir / "checkpoints"),
            num_train_epochs=config.num_epochs,
            per_device_train_batch_size=config.per_device_train_batch_size,
            gradient_accumulation_steps=config.gradient_accumulation_steps,
            warmup_steps=config.warmup_steps,
            learning_rate=config.learning_rate,
            weight_decay=config.weight_decay,
            bf16=True,
            fp16=False,
            logging_steps=1,
            optim="adamw_8bit",
            lr_scheduler_type="linear",
            seed=42,
            report_to="none",
        ),
    )

    logger.info("Starting training...")
    trainer.train()

    lora_output = str(output_dir / "lora_adapter")
    logger.info(f"Saving LoRA adapter to {lora_output}")
    model.save_pretrained(lora_output)
    tokenizer.save_pretrained(lora_output)

    gguf_output = str(output_dir / "gguf_export")
    logger.info(f"Saving GGUF to {gguf_output}")
    model.save_pretrained_gguf(gguf_output, tokenizer, quantization_method="q4_k_m")

    logger.info("Training complete!")
    return 0


if __name__ == "__main__":
    exit(main())
