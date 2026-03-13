# Model Pre-flight Checklist

Before committing to a multi-day LLM production run.

## Table of Contents

- [Consideration](#consideration)
- [Evaluation — Quality](#evaluation--quality)
- [Evaluation — Speed](#evaluation--speed)

---

## Consideration - Speed and Quality

Speed and quality considerations before selecting a model.

| # | Check                                 | Notes                                                                  |
|---|---------------------------------------|------------------------------------------------------------------------|
| 1 | **Model size**                        | 3b / 8b / 24b / 32b — fits in 24GB VRAM?                               |
| 2 | **Avoid reasoning/thinking models**   | ~10x slower — cannot finish millions of records                        |
| 3 | **MoE model?**                        | Can run larger model on lower VRAM                                     |
| 4 | **Parallel/batch processing support** | vllm                                                                   |
| 5 | **NVFP4 support**                     | Faster inference on Blackwell GPUs — check model is available in NVFP4 |

---

## Evaluation — Quality

Run on representative records, review output files.

```text
[10 representative records]
    |
    +-- tool001__model_eval --> _output_md/  (input + output per record)
    |
    +-- Kimi k2.5: verify extraction accuracy against webtext
```

| Check                  | What to verify                                                        |
|------------------------|-----------------------------------------------------------------------|
| **Label order**        | Categories in correct order (verification script)                     |
| **Mandatory content**  | All required fields present (verification script)                     |
| **Extraction quality** | Kimi k2.5 reviews input/output files — is extracted content accurate? |

---

## Evaluation — Speed

| Check                 | What to verify                                       | Notes                                                         |
|-----------------------|------------------------------------------------------|---------------------------------------------------------------|
| **GPU utilisation**   | ~100% in task manager during inference               |                                                               |
| **Inference speed**   | Fast responses, no long pauses                       |                                                               |
| **Token consumption** | Input/output within limits                           | Exceeding limit causes vllm crash — ollama handles gracefully |
| **Parallel/batch**    | vllm can actually finish the work                    | Known issue: vllm can crash mid-run                           |
| **NVFP4 activated**   | Confirm NVFP4 is actually in use, not just supported | On paper ≠ activated at runtime                               |
| **VRAM releasing**    | VRAM freed after processing                          | vllm holds VRAM — ollama releases after done                  |
