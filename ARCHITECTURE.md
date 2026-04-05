# Architecture

## System Overview

This project fine-tunes **Qwen2.5-0.5B-Instruct** using **QLoRA** for structured information extraction from unstructured text (resumes, product descriptions, LinkedIn bios), with a production-grade guardrails system for output validation.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        INFERENCE PIPELINE                          │
│                                                                     │
│  ┌──────────┐    ┌────────────┐    ┌─────────────┐    ┌──────────┐ │
│  │ Raw Text │───▶│ Classifier │───▶│   Schema    │───▶│  Prompt  │ │
│  │  Input   │    │(rule-based)│    │  Registry   │    │ Template │ │
│  └──────────┘    └────────────┘    └─────────────┘    └────┬─────┘ │
│                                                            │       │
│                                                            ▼       │
│                                                    ┌──────────────┐│
│                                                    │ Qwen2.5-0.5B ││
│                                                    │  + LoRA      ││
│                                                    └──────┬───────┘│
│                                                           │        │
│                                                           ▼        │
│  ┌──────────┐    ┌─────────────────────────────────────────────┐   │
│  │ Validated │◀───│           GUARDRAILS SYSTEM                │   │
│  │   JSON   │    │                                             │   │
│  │  Output  │    │  Layer 1: JSON Validity Check               │   │
│  └──────────┘    │  Layer 2: Schema Validation (required keys) │   │
│       ▲          │  Layer 3: Field Restriction (no extras)     │   │
│       │          │  Layer 4: Type Checking                     │   │
│       │          │                                             │   │
│       │          │  ✗ Invalid → Smart Retry (≤3 attempts)     │   │
│       │          │    (passes error feedback to model)         │   │
│       │          └─────────────────────────────────────────────┘   │
│       │                           │                                │
│       │                    ┌──────▼──────┐                        │
│       └────────────────────│  Inference  │                        │
│                            │    Logger   │                        │
│                            └─────────────┘                        │
└─────────────────────────────────────────────────────────────────────┘
```

## Model Selection

### Why Qwen2.5-0.5B-Instruct?

| Factor | Detail |
|--------|--------|
| **Size** | 0.5B parameters (~1GB FP16, ~300MB 4-bit quantized) |
| **Instruction Following** | Pre-trained on instruction-following data, strong baseline for structured tasks |
| **QLoRA Compatibility** | Fits entirely in Colab free T4 GPU (16GB VRAM) with 4-bit quantization |
| **Inference Speed** | Fast inference even on CPU with 16GB RAM |
| **Community Support** | Well-supported by HuggingFace, PEFT, and TRL ecosystems |

### Trade-offs

| Advantage | Limitation |
|-----------|-----------|
| Fast training (~15 min on T4) | Weaker complex reasoning vs 7B+ models |
| Low resource requirements | May struggle with ambiguous/noisy inputs |
| Easy deployment | Limited context understanding for very long text |
| Cost-effective | Needs more structured prompting to produce reliable output |

## Fine-tuning Approach: QLoRA

### Why QLoRA over Full Fine-tuning?

| Aspect | Full Fine-tuning | QLoRA |
|--------|-----------------|-------|
| Memory | ~2GB+ (FP16) | ~500MB (4-bit + adapters) |
| Trainable params | 494M (100%) | ~1.5M (~0.3%) |
| Training time | Longer | 3-5x faster |
| Quality | Marginally better | Comparable for task-specific tuning |
| Adapter size | Full model copy | ~10-50MB LoRA weights |

### QLoRA Configuration

```
LoRA rank (r): 16
LoRA alpha: 32
Dropout: 0.05
Target modules: q_proj, v_proj, k_proj, o_proj
Quantization: 4-bit NF4 with double quantization
```

## Dataset Design

### Strategy: Self-Created Synthetic Dataset

**Why synthetic?**
- **Deterministic**: Every output is guaranteed valid JSON
- **Controlled**: Perfect schema consistency across all samples
- **Scalable**: Can generate any number of samples instantly
- **No licensing issues**: Fully self-created

### Categories

| Category | Samples | Schema Fields |
|----------|---------|---------------|
| Resume | 500 | name, role, experience, skills, education |
| Product | 300 | product_name, brand, price, features, colors |
| Bio | 200 | name, role, company, previous_companies, experience, skills, education |

### Data Variations (Robustness)
- **10+ sentence templates** per category to avoid overfitting
- **Shuffled sentence order** within templates
- **10% field omission** (random optional fields set to null)
- **Large random pools**: 100+ names, 50+ skills, 30+ roles

### Format: Alpaca-style Instruction Tuning

```json
{
  "instruction": "Extract structured information from the following text and return valid JSON.",
  "input": "<unstructured text>",
  "output": "<valid JSON>",
  "category": "resume"
}
```

## Guardrails System

### Why Guardrails?

Small language models (0.5B) can produce:
- Invalid JSON (missing brackets, trailing commas)
- Extra hallucinated fields not in the schema
- Wrong data types (string instead of list)
- Missing required fields

Guardrails catch these errors post-generation, ensuring **production-grade reliability**.

### 4-Layer Validation

1. **JSON Validity**: Parses output with `json.loads()`, handles markdown code block extraction
2. **Schema Validation**: Checks all required fields exist per category schema
3. **Field Restriction**: Rejects unexpected/hallucinated fields
4. **Type Checking**: Validates field value types (str, list, null)

### Smart Retry Mechanism

On validation failure, the system:
1. Collects specific error messages
2. Constructs a retry prompt with error feedback
3. Re-runs the model (up to 3 retries)
4. Returns validated output or best-effort with error report

### Error Taxonomy

All errors are classified into 4 categories for structured debugging:
- `invalid_json`: Output cannot be parsed as JSON
- `missing_field`: Required schema field is absent
- `extra_field`: Field not defined in schema
- `wrong_type`: Field value has incorrect data type

## Evaluation Strategy

### 3-Way Comparison

| Configuration | Purpose |
|--------------|---------|
| Base Model | Baseline performance without fine-tuning |
| Fine-tuned | Impact of QLoRA fine-tuning |
| Fine-tuned + Guardrails | Full pipeline with validation |

### Metrics

- **JSON Validity Rate**: % of outputs parseable as JSON
- **Exact Match Accuracy**: % matching ground truth exactly
- **Field-level Precision/Recall/F1**: Per-field correctness
- **Retry Rate**: % of samples needing retries
- **Retry Success Rate**: % of retries that fixed the output
- **Error Taxonomy**: Distribution of error types

## Input Classification

A lightweight **rule-based classifier** routes inputs to the correct schema:

- Keyword matching against domain-specific terms
- Special heuristics (e.g., `$` → product, `|` separators → bio)
- Fallback to "resume" for ambiguous inputs

This avoids requiring the user to specify input type manually.

## Project Structure

```
fine_tuning_SLM/
├── src/
│   ├── config.py        # Centralized config, schemas, prompts
│   ├── classifier.py    # Input type detection
│   ├── formatting.py    # Chat template formatting
│   ├── guardrails.py    # 4-layer validation + retry
│   ├── train.py         # Training pipeline
│   └── inference.py     # Inference with logging
├── data/
│   ├── generate_dataset.py
│   ├── raw/             # Full generated dataset
│   ├── processed/       # Train/val/test splits
│   └── sample_dataset.json
├── evaluation/
│   ├── eval.py          # 3-way comparison
│   └── results.json     # Saved metrics
├── notebooks/
│   └── training.ipynb   # Colab-ready notebook
├── demo/
│   └── demo_video.mp4
├── README.md
├── ARCHITECTURE.md
└── requirements.txt
```
