---
base_model: Qwen/Qwen2.5-0.5B-Instruct
library_name: peft
pipeline_tag: text-generation
tags:
- base_model:adapter:Qwen/Qwen2.5-0.5B-Instruct
- lora
- sft
- transformers
- trl
---

# Qwen2.5-0.5B Structured Extraction LoRA Adapter

QLoRA adapter fine-tuned on 1000 synthetic samples for structured information extraction (resumes, product descriptions, LinkedIn bios).

## Training Details

- **Base model:** Qwen/Qwen2.5-0.5B-Instruct
- **Method:** QLoRA (4-bit NF4, double quantization)
- **LoRA config:** r=16, alpha=32, dropout=0.05
- **Target modules:** q_proj, v_proj, k_proj, o_proj
- **Epochs:** 3
- **Learning rate:** 2e-4
- **Hardware:** Google Colab T4 GPU

## Framework versions

- PEFT 0.18.1
