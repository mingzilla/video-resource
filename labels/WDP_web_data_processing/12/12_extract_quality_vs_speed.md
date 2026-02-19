### How LLM Processing works

- Prefill: Processes the full input prompt in parallel, compute-intensive, high GPU utilization
- Decode: Autoregressive token generation, memory bandwidth-bound, lower GPU utilization

```text
Prefill:  ████████████████████  Compute-bound (matmuls, FLOPs maxed)
          GPU: ~100% utilization
          "Using all the CUDA cores"

Decode:   ░░░░░░░░░░░░░░░░░░░░  Memory bandwidth-bound
          GPU: ~10-30% utilization  
          "Waiting on VRAM → cache transfers, compute idle"


 Prefill     Decode
 [AAAAAA] -> [AA    ]
                |  |
                BB |
                   CC
```

```text
Prefill:  [A] → [B] → [C]  (sequential, even with NVFP4)
Decode:   [A1+B1] → [A2+B2] → [A3+B3]  (batched together)
```

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
