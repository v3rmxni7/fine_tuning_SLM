# Fine-tuning a Small Language Model for Structured Information Extraction

Fine-tune **Qwen2.5-0.5B-Instruct** using **QLoRA** to extract structured JSON from unstructured text (resumes, product descriptions, LinkedIn bios) — with a production-grade guardrails system.

## Architecture Diagram

```
┌──────────────┐     ┌────────────┐     ┌──────────────┐     ┌─────────────┐
│  Unstructured│────▶│  Input     │────▶│  Prompt      │────▶│ Qwen2.5-0.5B│
│  Text Input  │     │  Classifier│     │  Construction│     │  + LoRA     │
└──────────────┘     └────────────┘     └──────────────┘     └──────┬──────┘
                                                                    │
                                                                    ▼
┌──────────────┐     ┌─────────────────────────────────────────────────────┐
│  Structured  │◀────│                GUARDRAILS SYSTEM                   │
│  JSON Output │     │  Layer 1: JSON Validity    Layer 3: Field Restrict │
└──────────────┘     │  Layer 2: Schema Validate  Layer 4: Type Check    │
                     │                                                     │
                     │  ✗ Invalid → Smart Retry with error feedback (≤3) │
                     └─────────────────────────────────────────────────────┘
```

## What It Does

**Input:** Unstructured natural language text
```
Sarah Chen is a senior data engineer with 5 years of experience in
Apache Spark, Python, and AWS. She holds a Master's in CS from Stanford.
```

**Output:** Validated structured JSON
```json
{
  "name": "Sarah Chen",
  "role": "Senior Data Engineer",
  "experience": "5 years",
  "skills": ["Apache Spark", "Python", "AWS"],
  "education": "Master's in CS from Stanford"
}
```

Supports 3 categories: **Resume**, **Product Description**, **LinkedIn Bio** — automatically classified.

## Guardrails System

The guardrails system ensures production-grade output reliability from a small 0.5B model.

### Why Guardrails?

Small language models can produce invalid JSON, hallucinate extra fields, use wrong data types, or omit required fields. Guardrails catch and correct these issues.

### 4 Validation Layers

| Layer | What It Does | Example Failure |
|-------|-------------|-----------------|
| **JSON Validity** | Ensures output parses as valid JSON | `{name: "John"` (missing bracket) |
| **Schema Validation** | Checks all required fields exist | Missing `skills` field |
| **Field Restriction** | Rejects unexpected/hallucinated fields | Extra `hobby` field |
| **Type Checking** | Validates field value types | `skills` as string instead of list |

### Smart Retry

When validation fails, the system passes specific error feedback to the model:
```
Your previous output was invalid.
Errors:
- Field 'skills' should be list, got string
- Unexpected field: 'hobby'
Fix the output and return valid JSON only.
```

Up to 3 retry attempts. If all fail, returns best-effort output with error report.

### Error Taxonomy

All errors are classified for structured debugging:
- `invalid_json` — Cannot parse as JSON
- `missing_field` — Required field absent
- `extra_field` — Hallucinated field
- `wrong_type` — Incorrect data type

## Setup Instructions

### Prerequisites
- Python 3.10+
- CUDA GPU (for training) — Google Colab T4 recommended
- 16GB RAM (for CPU inference)

### 1. Clone and Install

```bash
git clone https://github.com/v3rmxni7/fine_tuning_SLM.git
cd fine_tuning_SLM
pip install -r requirements.txt
```

### 2. Generate Dataset

```bash
python data/generate_dataset.py
```

This creates 1000 synthetic samples (800 train / 100 val / 100 test).

### 3. Train (Google Colab)

Open `notebooks/training.ipynb` in Google Colab with a **T4 GPU** runtime and run all cells.

Or run locally with a GPU:
```bash
python -m src.train
```

### 4. Run Inference

```bash
python -m src.inference
```

### 5. Evaluate

```bash
python evaluation/eval.py
```

## Model Details

| Aspect | Detail |
|--------|--------|
| **Base Model** | Qwen2.5-0.5B-Instruct |
| **Fine-tuning** | QLoRA (4-bit NF4 quantization) |
| **LoRA Config** | r=16, alpha=32, dropout=0.05 |
| **Target Modules** | q_proj, v_proj, k_proj, o_proj |
| **Training** | 3 epochs, lr=2e-4, batch=4, grad_accum=4 |
| **Dataset** | 1000 self-created synthetic samples |

## Evaluation: 3-Way Comparison

| Metric | Base Model | Fine-tuned | Fine-tuned + Guardrails |
|--------|-----------|------------|------------------------|
| JSON Validity | 4% | 100% | 100% |
| Exact Match | 0% | 91% | 91% |
| Field Precision | 0.70 | 0.9854 | 0.9854 |
| Field Recall | 0.65 | 0.9854 | 0.9854 |
| Field F1 | 0.6722 | 0.9854 | 0.9854 |
| Failure Rate | 96% | 0% | 0% |

Evaluated on 100 test samples. Full results in `evaluation/results.json`.

## Dataset

### Self-Created Synthetic Dataset (1000 samples)

| Category | Count | Schema |
|----------|-------|--------|
| Resume | 500 | name, role, experience, skills, education |
| Product | 300 | product_name, brand, price, features, colors |
| Bio | 200 | name, role, company, previous_companies, experience, skills, education |

### Robustness Features
- 10+ sentence templates per category
- Shuffled sentence order
- 10% random field omission (null values)
- Large random pools (100+ names, 50+ skills, 30+ roles)

## Project Structure

```
fine_tuning_SLM/
├── src/
│   ├── config.py           # Schema registry, prompts, hyperparameters
│   ├── classifier.py       # Rule-based input type detection
│   ├── formatting.py       # Chat template formatting
│   ├── guardrails.py       # 4-layer validation + smart retry
│   ├── train.py            # QLoRA training pipeline
│   └── inference.py        # Inference with logging
├── data/
│   ├── generate_dataset.py # Synthetic dataset generator
│   ├── raw/                # Full generated dataset
│   ├── processed/          # Train/val/test splits
│   └── sample_dataset.json # 50-sample preview
├── evaluation/
│   ├── eval.py             # 3-way comparison metrics
│   └── results.json        # Saved evaluation results
├── notebooks/
│   └── training.ipynb      # Colab-ready training notebook
├── demo/
│   └── demo_video.mp4      # Demo recording
├── ARCHITECTURE.md         # Detailed architecture documentation
├── README.md
└── requirements.txt
```

## Demo

### Normal Flow
Input text → Classifier detects category → Model generates JSON → Guardrails validate → Clean output

### Failure Cases / Guardrails Working
1. Base model produces invalid JSON → Guardrail catches → Retry fixes it
2. Model hallucinates extra fields → Field restriction blocks them
3. Wrong data types → Type checker catches → Retry with feedback

See `demo/demo_video.mp4` for full walkthrough.

## Failure Cases & Limitations

1. **Ambiguous inputs**: Text that doesn't clearly match any category may be misclassified
2. **Very long inputs**: Truncated at 512 tokens
3. **Non-English text**: Model primarily trained on English data
4. **Complex nested structures**: Schema is flat — nested JSON not supported
5. **Null field detection**: Model may hallucinate values for genuinely absent fields

## Tech Stack

- **Python 3.10+**
- **HuggingFace Transformers** — model loading and generation
- **PEFT** — QLoRA adapter management
- **BitsAndBytes** — 4-bit quantization
- **TRL** — SFTTrainer for instruction tuning
- **Datasets** — data loading and processing
