# Fine-Tuning Plan: Company Extraction Model

- Goal and Why
- Training Data Format and Why + Example
- Training Template and Why
- Output Format and Why
- Training Setup
- Data Quality

## Goal

Train a small, fast, specialised model to extract structured company information
from raw webtext — replacing `qwen2.5:32b` (10s/record) with a fine-tuned 3B
model (~1.5s/record) that produces an identical output structure.

---

## Why Fine-Tune Instead of Prompt Engineering

| Approach                 | Speed       | Cost      | Quality            |
|--------------------------|-------------|-----------|--------------------|
| `qwen2.5:32b` zero-shot  | 10s/record  | High VRAM | Good               |
| `llama3.2:3b` zero-shot  | 1.5s/record | Low VRAM  | Poor               |
| Fine-tuned `llama3.2:3b` | 1.5s/record | Low VRAM  | Good (specialised) |

Teacher-student distillation: use the big model to generate labelled training
data, then fine-tune the small model on those examples.

**Why `qwen2.5:3b` over `llama3.2:3b`:** same model family as the teacher
(`qwen2.5:32b`), so the student converges faster and learns better.

---

## Training Data Format

### Message Structure (one record = one JSONL line)

```
┌─────────────────────────────────────────────────────────┐
│  role: system                                           │
│  "Extract company information from the website          │
│   content in British English."                          │
├─────────────────────────────────────────────────────────┤
│  role: user                                             │
│  <raw webtext>                                          │
├─────────────────────────────────────────────────────────┤
│  role: assistant                                        │
│  INDUSTRIES: ...                                        │
│  ACTIVITIES: ...                                        │
│  PRODUCTS: ...                                          │
│  ...                                                    │
└─────────────────────────────────────────────────────────┘
```

This is identical to the conversation history submitted to an LLM. Fine-tuning
teaches the model: "when you see this system + user pattern, produce this
assistant response."

### Why This Format (Option B)

Three options were considered:

| Option         | System message                     | User message | Inference cost |
|----------------|------------------------------------|--------------|----------------|
| A              | Full prompt template (~1900 chars) | webtext      | High           |
| **B** (chosen) | One-liner                          | webtext      | Low            |
| C              | None                               | webtext      | Lowest         |

**B is chosen because:**

- A one-liner anchors intent with near-zero token cost
- Small 3B models benefit from a clear signal ("what do I do with this text?")
- Without any system message, the model must infer intent from training alone —
  risky for a small model, even if technically possible

**Note on the "webtext before prompt" trick (from current pipeline):**
The existing pipeline appends the prompt *after* the webtext so the distance
from webtext to generated tokens is fixed. This helps zero-shot/few-shot
generation maintain field order. For fine-tuning, this positional trick is
unnecessary — the model learns the output structure directly from examples.

---

## Output Format Rules

### Always emit every label, even if empty

```
INDUSTRIES: Advanced Materials, Paper & Packaging
ACTIVITIES:
PRODUCTS: Electrolyser Coatings, Moulded Fibre
SERVICES:
MARKETS: Automotive, Aerospace
REGIONS: Global
MODEL: B2B
COMPANY_SUMMARY: James Cropper PLC is a market leader...
COMPANY_SHORT_SUMMARY: James Cropper PLC is a market leader...
COMPANY_LONG_SUMMARY: James Cropper PLC is a market leader...
COMPANY_TRADING_NAME: James Cropper PLC
IS_MANUFACTURING: true
MANUFACTURING_PROCESSES: Fibre technology, electrochemical coatings
TECHNICAL_CAPABILITIES: CupCycling facility, electrolyser coating development
```

**Why always include empty labels:**

| Concern              | Result                                               |
|----------------------|------------------------------------------------------|
| Training consistency | Model sees identical N-line structure every record   |
| Output parsing       | Always split on `\n`, no missing-key handling needed |
| Structure locking    | Model never makes a decision about what to include   |

### How the model learns "required" vs "optional"

The model has no concept of required/optional. It learns from frequency:

```
COMPANY_SUMMARY in 1000/1000 records  →  model always produces it
SERVICES        in 1000/1000 records  →  model always produces it (even if empty)
```

This is why always-including-empty-labels is critical — without it, the model
learns to sometimes skip labels, and that's a probabilistic decision it can
get wrong.

---

## Training Setup

| Parameter          | Value                     |
|--------------------|---------------------------|
| Base model         | `qwen2.5:3b`              |
| Fine-tuning method | QLoRA (quantised LoRA)    |
| Tool               | unsloth                   |
| Hardware           | RTX 5090 laptop 24GB VRAM |
| Target records     | ~1000                     |
| Negative examples  | Not needed                |

**Why no negative examples:**
Negative examples are used in DPO/RLHF for preference learning ("prefer output A over output B").
For supervised fine-tuning (SFT), only good examples are needed.
The model learns the distribution of correct outputs and never sees bad ones.

**Inference speed after fine-tuning:**
~1.5s/record (same as base model — fine-tuning changes weights, not architecture).

### Comparison table (Ollama pull vs our fine-tuned version):

| Factor            | ollama pull llama3.2:3b          | our fine-tuned version                 |
|-------------------|----------------------------------|----------------------------------------|
| base model        | meta-llama/Llama-3.2-3B-Instruct | unsloth/Llama-3.2-3B-Instruct (same)   |
| parameters        | 3.2B                             | 3.2B                                   |
| context length    | 131072                           | 131072                                 |
| embedding length  | 3072                             | 3072                                   |
| format            | GGUF                             | GGUF                                   |
| quantisation      | Q4_K_M                           | Q4_K_M                                 |
| source            | Ollama registry                  | trained locally → exported via unsloth |
| weights           | base instruct weights only       | base weights + LoRA adapter merged     |
| system prompt     | none baked in                    | one-liner baked into Modelfile         |
| ollama model name | llama3.2:3b                      | company-extractor:llama3.2-3b-v01      |

---

## Data Quality

The quality of the data decides the quality of the model. Considerations:

- Validate training data using frontier model
- Bad data - fix or exclude
