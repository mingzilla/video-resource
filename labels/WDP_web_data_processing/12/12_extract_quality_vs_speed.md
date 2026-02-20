## Reasons and Options

|       | 1m token | 1m items |
|-------|----------|----------|
| HTTP  | 0.05 usd |          |
| Hire  |          |          |
| Local | 0        | 0        |

Note: 8k tokens per item

### How LLM Processing works

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

---

## Other models tried

- docker-compose.gemma-2-2b.yml
- docker-compose.qwen2.5-1.5b.yml
- docker-compose.qwen2.5-3b.yml

Comments - Results are shocking

- Labels cannot maintain order
- Too slow