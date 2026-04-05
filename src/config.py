MODEL_NAME = "Qwen/Qwen2.5-0.5B-Instruct"
MAX_SEQ_LENGTH = 512

LORA_R = 16
LORA_ALPHA = 32
LORA_DROPOUT = 0.05
LORA_TARGET_MODULES = ["q_proj", "v_proj", "k_proj", "o_proj"]

LEARNING_RATE = 2e-4
NUM_EPOCHS = 3
BATCH_SIZE = 4
GRADIENT_ACCUMULATION_STEPS = 4
WARMUP_RATIO = 0.1
WEIGHT_DECAY = 0.01
LOGGING_STEPS = 10
EVAL_STEPS = 50
SAVE_STRATEGY = "epoch"
FP16 = True

TRAIN_FILE = "data/processed/train.json"
VAL_FILE = "data/processed/val.json"
TEST_FILE = "data/processed/test.json"
SAMPLE_FILE = "data/sample_dataset.json"
OUTPUT_DIR = "outputs"
ADAPTER_DIR = "outputs/lora_adapter"
EVAL_RESULTS_FILE = "evaluation/results.json"
INFERENCE_LOG_FILE = "evaluation/inference_logs.json"

MAX_RETRIES = 3

SCHEMA_REGISTRY = {
    "resume": {
        "required_fields": ["name", "role", "experience", "skills", "education"],
        "field_types": {
            "name": str,
            "role": str,
            "experience": str,
            "skills": list,
            "education": str,
        },
    },
    "product": {
        "required_fields": ["product_name", "brand", "price", "features", "colors"],
        "field_types": {
            "product_name": str,
            "brand": str,
            "price": str,
            "features": list,
            "colors": list,
        },
    },
    "bio": {
        "required_fields": ["name", "role", "company", "previous_companies", "experience", "skills", "education"],
        "field_types": {
            "name": (str, type(None)),
            "role": str,
            "company": str,
            "previous_companies": list,
            "experience": str,
            "skills": list,
            "education": str,
        },
    },
}

SYSTEM_PROMPT = """You are an information extraction system.

Rules:
- Output STRICT JSON only. No explanation, no markdown, no extra text.
- Follow the schema exactly. No extra fields.
- If a field is not present in the input, return null for that field.

Schema:
{schema}"""

EXTRACTION_INSTRUCTION = "Extract structured information from the following text and return valid JSON."

RETRY_PROMPT = """Your previous output was invalid.

Errors:
{errors}

Fix the output and return valid JSON only. Follow the schema exactly."""


def get_schema_fields_str(category):
    """Build a human-readable schema string to embed in the prompt."""
    schema = SCHEMA_REGISTRY[category]
    lines = []
    for field, ftype in schema["field_types"].items():
        if ftype == list:
            type_str = "list of strings"
        elif ftype == (str, type(None)):
            type_str = "string or null"
        else:
            type_str = "string"
        lines.append(f'  "{field}": {type_str}')
    return "{\n" + ",\n".join(lines) + "\n}"
