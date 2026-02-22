## Prompt and Model

```text
                   +---------------+
 [Samples]|  ----> | webtext       |
 ---------+        | ~~            |
                   | ~~            |
                   |   capability  | + [prompt_template.md] --> capability
                   | ~~~           |                        LLM
                   | ~~~~~         |
                   +---------------+
```

| Aspect                  | Qwen 14b        | Qwen 32b     | Llama 3.2:3b |
|-------------------------|-----------------|--------------|--------------|
| **Speed**               | Faster          | Slower       | Fastest      |
| **Format compliance**   | Good            | Better       | Poor         |
| **Category separation** | Mixed           | Better       | Poor         |
| **Inference control**   | Some leakage    | Less leakage | High leakage |
| **Summary quality**     | Good            | Good         | Mixed        |
| **Overall**             | ⚠️ **Marginal** | ✅ **Best**   | ❌ **Avoid**  |

---

## 1 Million Record Cost Estimate

|              | 1m token      | apx Cost/Hour | apx s/Item | 1m items    |
|--------------|---------------|---------------|------------|-------------|
| HTTP         | 0.03 usd      | N/A           | —          | 240 usd     |
| Hire RTX5090 | **0.021 usd** | 0.80          | 0.75s      | **166 usd** |
| Hire H20     | **0.026 usd** | 2.00          | 0.38s      | **104 usd** |
| Hire H100    | **0.010 usd** | 2.50          | 0.15s      | **83 usd**  |
| Local        | 0             | N/A           | 0.75s      | 0           |

Note: 8k tokens per item
Estimated performance by Kimi and ChatGPT: H20=2x5090, H100=5x5090

---

## How LLM Processing works

```text
          Prefill     Decode
  text -> [AAAAAA] -> [AA    ]
                         |  |
                         BB |
                            CC
```

|            | input   | output |
|------------|---------|--------|
| processing | prefill | decode |
| bottleneck | gpu     | vram   |

- Prefill: Processes the full input prompt in parallel, compute-intensive, high GPU utilization
- Decode: Autoregressive token generation, memory bandwidth-bound, lower GPU utilization

---

## Performance

|               | 60 items speed | avg speed per item |
|---------------|----------------|--------------------|
| vllm single   | 180s           | 3s                 |
| vllm batching | 45s            | 0.75s              |
| ollama single | 90s            | 1.5s               |

### How NVFP4 works

- Each bit is 0 or 1
- FP4 means: each value has 4 bits
- FP16 means: each value has 16 bits
- so for the same size of data transition e.g. 16mb, assuming it 64 bits bus bandwidth, fp4 has a shorter queue to move the data through than fp16 then

| Format  | Bits per Value | Example Value    | Values in 16MB | "Queue Length" for Same Compute |
|---------|----------------|------------------|----------------|---------------------------------|
| FP16    | 16             | 0001000100010001 | 8 million      | Longer queue                    |
| FP8     | 8              | 00010001         | 16 million     | Medium queue                    |
| **FP4** | **4**          | 0001             | **32 million** | **Shorter queue**               |

```text
FP16:  [VRAM] ======== 16MB ========> [Tensor Cores]  (wait...)
       8M values @ 16-bit each

FP4:   [VRAM] ==== 4MB ====> [Tensor Cores]  (done, next!)
       8M values @ 4-bit each
```

### FlashAttention

FlashAttention is an algorithmic optimization for the attention mechanism in Transformers

| Version               | Year | Key Innovation                          | GPU Utilization | Speed vs Vanilla          |
|-----------------------|------|-----------------------------------------|-----------------|---------------------------|
| **FlashAttention v1** | 2022 | Tiling + online softmax                 | ~25% (A100)     | 3-4× faster               |
| **FlashAttention v2** | 2023 | Better parallelism, deferred softmax    | 50-70% (A100)   | **2× v1**                 |
| **FlashAttention v3** | 2024 | Asynchronous execution, FP8/FP4 support | **75% (H100)**  | **2× v2, 1.2 PFLOPS FP8** |
