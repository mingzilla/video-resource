# CUDA GPU Acceleration

- CUDA
- GPU and Performance
- CUDA Integration
- GPU Layer Offloading

```
[CUDA = Compute Unified Device Architecture]
    |
    +-- NVIDIA GPU programming platform
    +-- Means: A unified coding solution to make use of gpu (same code for ada or blackwell etc, different drivers)
    +-- Enables parallel processing on GPU
    +-- Used by all frameworks for GPU acceleration
```

---

## GPU and Performance

### NVIDIA Naming Logic (Simplified)

#### **The first two digits = generation**

- **40‑series** -> Ada Lovelace
- **50‑series** -> Blackwell
- **60‑series** -> future gen after Blackwell

#### **The last two digits = performance tier**

| Tier   | Meaning            | Examples   |
|--------|--------------------|------------|
| **90** | **Ultra-flagship** | 4090, 5090 |
| **80** | **High-end**       | 4080, 5080 |
| **70** | **Upper-midrange** | 4070, 5070 |
| **60** | **Midrange**       | 4060, 5060 |
| **50** | **Entry-level**    | 4050, 5050 |

**~90 > ~80 > ~70 > ~60 > ~50**

### GPU Comparison Table (Specs & Performance)

| GPU          | VRAM      | Memory Type | Memory Bandwidth | CUDA Cores | Perf. Score (Gaming)              |
|--------------|-----------|-------------|------------------|------------|-----------------------------------|
| **RTX 4070** | **12 GB** | **GDDR6X**  | **504 GB/s**     | **5,888**  | **~60**                           |
| **RTX 4090** | **24 GB** | **GDDR6X**  | **1008 GB/s**    | **16,384** | **~92**                           |
| **RTX 5070** | **12 GB** | **GDDR7**   | **672 GB/s**     | **6,144**  | **~64**                           |
| **RTX 5090** | **32 GB** | **GDDR7**   | **1792 GB/s**    | **21,760** | **~2× 4090** (per BPC benchmarks) |

---

## CUDA Integration

**CUDA Integration by Framework:**

```text
[PyTorch]
    |
    +-- Uses cuBLAS, cuDNN (CUDA libraries)
    +-- tensor.cuda() moves data to GPU
    +-- Automatic GPU kernel selection
    |
    v
[CUDA GPU Execution]

[vLLM]
    |
    +-- Custom CUDA kernels for PagedAttention
    +-- Highly optimized matrix operations
    +-- Continuous batching on GPU
    |
    v
[CUDA GPU Execution]
```

```text
[llama.cpp]
    |
    +-- cuBLAS for matrix multiplication (CUDA backend)
    +-- Custom CUDA kernels for optimized ops
    +-- Optional: full or partial GPU offloading
    +-- -ngl parameter (number of GPU layers)
    |
    v
[CUDA GPU Execution]

[LLamaSharp]
    |
    +-- Wraps llama.cpp CUDA backend
    +-- GpuLayerCount parameter in C# (maps to -ngl)
    +-- Same cuBLAS operations as llama.cpp
    |
    v
[CUDA GPU Execution via llama.cpp]
```

```text
[ONNX Runtime]
    |
    +-- CUDA Execution Provider
    +-- Uses cuDNN, TensorRT
    +-- Cross-platform GPU support
    |
    v
[CUDA GPU Execution]
```

## GPU Layer Offloading

**GPU Layer Offloading (different runtimes do this similarly but differently):**

```
[Model Layers]
    |
    +-- Layer 1  ----+
    +-- Layer 2      |
    +-- ...          |--> GpuLayerCount: 100 --> [GPU Memory]
    +-- Layer 100 ---+
    +-- Layer 101 ----------------> [CPU Memory]
    +-- ...
    
Note:
- Neuron = input -> tokens -> algorithm((weight1 * token1), (w2 * t2), ..., bias) -> output
- Neuron and Parameter
  - Parameter: Weights, Biases
  - Neuron e.g.: has 1000 weights, 1 bias => 1001 params 
- Layer = [neuron1, neuron2, ...]

**[More Detailed Loading Decision Process]**
    |
    |-- model.gguf (20GB)
    |   |-- Contains: 200-layer neural network parameters
    |   |-- Each layer ≈ 100MB
    |   |-- Total size ≈ 20GB
    |
    |-- Your System:
    |   |-- GPU VRAM: 8GB
    |   |-- CPU RAM: 32GB
    |   |-- You need to decide: Where to place each layer?
    |
    v
**[Intelligent Decision]**
    |
    +-- Option A: All on CPU (20GB < 32GB ✓) -> Slow
    +-- Option B: All on GPU (20GB > 8GB ✗) -> Fail
    +-- Option C: GPU then CPU -> Best
    |
    v
**[Hybrid Solution Calculation]**
    |
    +-- GPU Available: 8GB
    +-- System Overhead: Reserve 1GB
    +-- Per Layer: 100MB
    +-- Number of Layers on GPU: (8GB - 1GB) / 100MB ≈ 70 layers
    |
    v
**[Final Loading]**
    |
    +-- Layers 1-70 -> GPU VRAM (7GB)
    +-- Layers 71-200 -> CPU RAM (13GB)
    +-- During Runtime: Data transfer between GPU <-> CPU required between layers 70 and 71
```
