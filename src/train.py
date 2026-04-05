import json
import torch
from datasets import Dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer

from src.config import (
    MODEL_NAME, MAX_SEQ_LENGTH,
    LORA_R, LORA_ALPHA, LORA_DROPOUT, LORA_TARGET_MODULES,
    LEARNING_RATE, NUM_EPOCHS, BATCH_SIZE, GRADIENT_ACCUMULATION_STEPS,
    WARMUP_RATIO, WEIGHT_DECAY, LOGGING_STEPS, EVAL_STEPS, SAVE_STRATEGY, FP16,
    TRAIN_FILE, VAL_FILE, OUTPUT_DIR, ADAPTER_DIR,
)
from src.formatting import format_chat_messages


def load_json(path):
    with open(path) as f:
        return json.load(f)


def prepare_training_data(samples, tokenizer):
    """Tokenize samples using the model's chat template."""
    formatted = []
    for sample in samples:
        category = sample.get("category", "resume")
        messages = format_chat_messages(sample, category)
        text = tokenizer.apply_chat_template(messages, tokenize=False)
        formatted.append({"text": text})
    return Dataset.from_list(formatted)


def setup_model_and_tokenizer():
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
    )

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
    )
    model = prepare_model_for_kbit_training(model)
    return model, tokenizer


def setup_lora(model):
    lora_config = LoraConfig(
        r=LORA_R,
        lora_alpha=LORA_ALPHA,
        lora_dropout=LORA_DROPOUT,
        target_modules=LORA_TARGET_MODULES,
        task_type="CAUSAL_LM",
        bias="none",
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()
    return model


def train():
    print("Loading model and tokenizer...")
    model, tokenizer = setup_model_and_tokenizer()

    print("Attaching LoRA adapters...")
    model = setup_lora(model)

    print("Preparing data...")
    train_data = load_json(TRAIN_FILE)
    val_data = load_json(VAL_FILE)
    train_dataset = prepare_training_data(train_data, tokenizer)
    val_dataset = prepare_training_data(val_data, tokenizer)
    print(f"  Train: {len(train_dataset)}, Val: {len(val_dataset)}")

    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        num_train_epochs=NUM_EPOCHS,
        per_device_train_batch_size=BATCH_SIZE,
        per_device_eval_batch_size=BATCH_SIZE,
        gradient_accumulation_steps=GRADIENT_ACCUMULATION_STEPS,
        learning_rate=LEARNING_RATE,
        warmup_ratio=WARMUP_RATIO,
        weight_decay=WEIGHT_DECAY,
        logging_steps=LOGGING_STEPS,
        eval_strategy="steps",
        eval_steps=EVAL_STEPS,
        save_strategy=SAVE_STRATEGY,
        fp16=FP16,
        report_to="none",
        remove_unused_columns=False,
        optim="paged_adamw_8bit",
    )

    trainer = SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        tokenizer=tokenizer,
        max_seq_length=MAX_SEQ_LENGTH,
    )

    print("Training started...")
    trainer.train()

    print(f"Saving LoRA adapter to {ADAPTER_DIR}...")
    model.save_pretrained(ADAPTER_DIR)
    tokenizer.save_pretrained(ADAPTER_DIR)
    print("Done.")


if __name__ == "__main__":
    train()
