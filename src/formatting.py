import json
from src.config import SYSTEM_PROMPT, EXTRACTION_INSTRUCTION, RETRY_PROMPT, get_schema_fields_str


def format_chat_messages(sample, category=None):
    """Build chat messages for training (includes assistant response)."""
    if category is None:
        category = sample.get("category", "resume")

    schema_str = get_schema_fields_str(category)
    system_msg = SYSTEM_PROMPT.format(schema=schema_str)

    return [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": f"{EXTRACTION_INSTRUCTION}\n\n{sample['input']}"},
        {"role": "assistant", "content": sample["output"]},
    ]


def format_inference_messages(text, category):
    """Build chat messages for inference (no assistant response)."""
    schema_str = get_schema_fields_str(category)
    system_msg = SYSTEM_PROMPT.format(schema=schema_str)

    return [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": f"{EXTRACTION_INSTRUCTION}\n\n{text}"},
    ]


def format_retry_messages(text, category, previous_output, errors):
    """Build chat messages for retry, including error feedback from guardrails."""
    schema_str = get_schema_fields_str(category)
    system_msg = SYSTEM_PROMPT.format(schema=schema_str)
    error_str = "\n".join(f"- {e}" for e in errors)
    retry_msg = RETRY_PROMPT.format(errors=error_str)

    return [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": f"{EXTRACTION_INSTRUCTION}\n\n{text}"},
        {"role": "assistant", "content": previous_output},
        {"role": "user", "content": retry_msg},
    ]


def load_and_format(path):
    """Load a JSON dataset and convert to training format with chat messages."""
    with open(path) as f:
        data = json.load(f)

    formatted = []
    for sample in data:
        category = sample.get("category", "resume")
        messages = format_chat_messages(sample, category)
        formatted.append({"messages": messages, "category": category})
    return formatted
