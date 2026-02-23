## Quality and Speed

```text
Quality - Models
Cost - HTTP, Hire, Local
Speed - How LLM works, NVFP4, FlashAttention
```

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

### vLLM v0.15.1 NVFP4 support for 50x0 NVidia Graphic Card Issue

| Card                      | Compute Capability | SM Version | Affected? |
|---------------------------|--------------------|------------|-----------|
| RTX 5090 (laptop/desktop) | 12.0               | SM120      | ✅ Yes     |
| **RTX 4000 Blackwell**    | **12.0**           | **SM120**  | **✅ Yes** |
| RTX 6000 Blackwell        | 12.0               | SM120      | ✅ Yes     |
| B200 (data center)        | 10.0               | SM100      | ❌ No      |

All **consumer/workstation Blackwell GPUs** use SM120, which vLLM's NVFP4 backend initially didn't recognize .

- vLLM v0.15.1 - Does not have NVFP4 support for **SM120** (compute capability 12.0) **Non MoE models**
- vLLM v0.15.1 - Only **MoE models** on SM120 got native NVFP4 support
- The general MXFP4 backend selection fix (PR #31089) that adds SM120 to the recognized list for **all model types** appears to still be pending or only in main branch.
