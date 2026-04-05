import json
import os
import time
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel

from src.config import MODEL_NAME, ADAPTER_DIR, MAX_RETRIES, MAX_SEQ_LENGTH, INFERENCE_LOG_FILE
from src.classifier import classify_input
from src.formatting import format_inference_messages, format_retry_messages
from src.guardrails import validate_output, get_error_summary


class InferencePipeline:

    def __init__(self, use_finetuned=True, use_guardrails=True, device="auto"):
        self.use_finetuned = use_finetuned
        self.use_guardrails = use_guardrails
        self.logs = []

        print(f"Loading {'fine-tuned' if use_finetuned else 'base'} model...")

        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        if torch.cuda.is_available():
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.float16,
            )
            self.model = AutoModelForCausalLM.from_pretrained(
                MODEL_NAME, quantization_config=bnb_config,
                device_map=device, trust_remote_code=True,
            )
        else:
            self.model = AutoModelForCausalLM.from_pretrained(
                MODEL_NAME, torch_dtype=torch.float32,
                device_map="cpu", trust_remote_code=True,
            )

        if use_finetuned:
            if os.path.exists(ADAPTER_DIR):
                print(f"Loading LoRA adapter from {ADAPTER_DIR}...")
                self.model = PeftModel.from_pretrained(self.model, ADAPTER_DIR)
            else:
                print(f"WARNING: adapter not found at {ADAPTER_DIR}, using base model")

        self.model.eval()
        print("Model ready.")

    def generate(self, messages):
        text = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=MAX_SEQ_LENGTH)
        inputs = {k: v.to(self.model.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs, max_new_tokens=256, do_sample=False,
                pad_token_id=self.tokenizer.pad_token_id,
            )

        input_len = inputs["input_ids"].shape[1]
        generated = outputs[0][input_len:]
        return self.tokenizer.decode(generated, skip_special_tokens=True).strip()

    def extract(self, text, category=None):
        """Full pipeline: classify -> generate -> validate -> retry if needed."""
        start_time = time.time()

        if category is None:
            category = classify_input(text)

        messages = format_inference_messages(text, category)
        raw_output = self.generate(messages)

        log_entry = {
            "input": text,
            "category": category,
            "raw_output": raw_output,
            "retries": 0,
            "errors": [],
            "final_output": None,
            "success": False,
            "guardrails_applied": self.use_guardrails,
            "time_seconds": 0,
        }

        if not self.use_guardrails:
            try:
                log_entry["final_output"] = json.loads(raw_output)
                log_entry["success"] = True
            except json.JSONDecodeError:
                log_entry["final_output"] = raw_output
            log_entry["time_seconds"] = round(time.time() - start_time, 2)
            self.logs.append(log_entry)
            return log_entry

        # validate with guardrails
        result = validate_output(raw_output, category)

        if result.is_valid:
            log_entry["final_output"] = result.data
            log_entry["success"] = True
            log_entry["time_seconds"] = round(time.time() - start_time, 2)
            self.logs.append(log_entry)
            return log_entry

        # retry with error feedback
        log_entry["errors"] = [e.to_dict() for e in result.errors]
        current_output = raw_output

        for attempt in range(MAX_RETRIES):
            error_msgs = get_error_summary(result.errors)
            retry_messages = format_retry_messages(text, category, current_output, error_msgs)
            current_output = self.generate(retry_messages)
            log_entry["retries"] = attempt + 1

            result = validate_output(current_output, category)
            if result.is_valid:
                log_entry["final_output"] = result.data
                log_entry["success"] = True
                break
            log_entry["errors"] = [e.to_dict() for e in result.errors]

        if not result.is_valid:
            log_entry["final_output"] = result.data or current_output

        log_entry["time_seconds"] = round(time.time() - start_time, 2)
        self.logs.append(log_entry)
        return log_entry

    def save_logs(self, path=None):
        path = path or INFERENCE_LOG_FILE
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(self.logs, f, indent=2, default=str)
        print(f"Saved {len(self.logs)} inference logs to {path}")


def main():
    pipeline = InferencePipeline(use_finetuned=True, use_guardrails=True)

    test_inputs = [
        "John Smith is a senior data scientist with 5 years of experience in Python, TensorFlow, and NLP. He holds a Master's in AI from Stanford.",
        "The ProBook Ultra is a laptop by TechCorp priced at $1299. It features 32GB RAM, 1TB SSD, and Intel i9. Available in silver and black.",
        "Engineering Manager at Google | Ex-Microsoft, Ex-Amazon | MBA from Harvard | Passionate about team building and system design | 12 years in tech",
    ]

    for i, text in enumerate(test_inputs):
        print(f"\n--- Example {i+1} ---")
        print(f"Input: {text[:100]}...")
        result = pipeline.extract(text)
        print(f"Category: {result['category']}")
        print(f"Success: {result['success']}, Retries: {result['retries']}")
        print(f"Output: {json.dumps(result['final_output'], indent=2)}")

    pipeline.save_logs()


if __name__ == "__main__":
    main()
