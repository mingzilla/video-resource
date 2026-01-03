# Model Formats and Frameworks Explanation

## Table of Contents

- **Model Formats**
    - HuggingFace Models (PyTorch, Tensorflow->JAX)
    - GGUF Models (llama.cpp - 1 file)
    - ONNX Models (cross platform)
- **Model Format -> Runner**
- **Complete Pipeline**
- **Summary**

## Model Format Hierarchy

```
[Original HuggingFace Model]
         |
         |-- Tokenizer - uses files (tokenizer.json, vocab.txt)
         |   |- runs an algorithm to split text, this uses tokenizer.json
         |   +- converts tokens into numbers, this uses vocab.txt
         |
         |-- Model config (config.json)
         |   |- a model must have config.json, regardless if trained by PyTorch or TensorFlow
         |   +- config.json describes the model architecture - e.g. num_hidden_layers
         |
         |-- Parameters: weights & biases
         |   |- **PyTorch** = framework for training/running ML models
         |   |- **Weights & biases** = the learned parameters
         |   +- **.bin / .safetensors** = PyTorch file formats that store parameters
         |
         +--CONVERT-->
                |
                +--[GGUF] (llama.cpp, LLamaSharp)
                |
                +--[ONNX] (ONNX Runtime, cross-platform)

Note:
(TensorFlow vs PyTorch) == (Angular vs React)
```

Typical release of a model includes:

- **Tokenizer** files (tokenizer.json, vocab.txt, etc.)
- **Config** (config.json)
- **PyTorch** weights (file format: .safetensors or .bin)
- Sometimes **GGUF** or **ONNX** conversions
    - (community-provided, not always official)
    - ONNX is a conversion format for deployment

## HuggingFace Models

```text
Google's AI Stack:
    |
    +- RESEARCH (New models):
    |       JAX + Flax/Haiku + TPUs
    |       |
    |       +-> Gemini, PaLM, Imagen, etc.
    |
    +- PRODUCTION (Deployment):
    |       TensorFlow (TF Serving, TF Lite, TF.js)
    |       |
    |       +-> Google Search, Photos, Translate, etc.
    |
    +- PARTNERS/CLOUD:
            TensorFlow Enterprise (for GCP customers)
            PyTorch on GCP (to accommodate market demand)

JAX
- JAX isn't an acronym
- Unofficial saying: Just After XLA (Accelerated Linear Algebra - Google's compiler for ML)
```

## GGUF Models - (llama.cpp specific)

**GGUF = GPT-Generated Unified Format**

**Created by and for llama.cpp**, GGUF is a binary format designed for efficient model loading and inference.

| Aspect             | Description                                            |
|--------------------|--------------------------------------------------------|
| **Purpose**        | Efficient inference format for llama.cpp ecosystem     |
| **Created By**     | llama.cpp project (Georgi Gerganov)                    |
| **Optimization**   | CPU-optimized with optional GPU acceleration           |
| **Quantization**   | Supports multiple precision levels (f16, q4, q8, etc.) |
| **Self-Contained** | Model weights + metadata in single file                |
| **File Size**      | Smaller than original PyTorch models                   |

**GGUF Structure:**

```
[GGUF File]
    |
    +-- Header (metadata)
    |     |
    |     +-- Model architecture
    |     +-- Tensor info
    |     +-- Hyperparameters
    |
    +-- Tensor Data (weights)
          |
          +-- Quantized or full precision
          +-- Layer-by-layer weights
```

**Used By:**

```
[GGUF]
    |
    +-- llama.cpp (C++ inference engine - the original)
    |     |
    |     +-- Direct C++ usage
    |     +-- CLI tools (llama-cli, llama-server)
    |     +-- Conversion tools (llama-convert-hf-to-gguf)
    |
    +-- LLamaSharp (C# wrapper around llama.cpp)
    +-- koboldcpp (GUI/API wrapper around llama.cpp)
    +-- text-generation-webui (supports llama.cpp backend)
    +-- llama-cpp-python (Python bindings for llama.cpp)
```

## ONNX Models - (cross platform)

**ONNX = Open Neural Network Exchange**

| Aspect               | Description                                      |
|----------------------|--------------------------------------------------|
| **Purpose**          | Cross-platform, cross-framework inference        |
| **Portability**      | Run on any ONNX Runtime (CPU, GPU, mobile, edge) |
| **Optimization**     | Hardware-specific optimizations                  |
| **Interoperability** | Convert between PyTorch, TensorFlow, etc.        |

**ONNX Runtime** is like the **JVM/JRE** for ONNX models - it’s the runtime that executes the model on different platforms.

### **Java Analogy:**

| Java World               | ONNX World               |
|--------------------------|--------------------------|
| `.java` source           | PyTorch/TF trained model |
| `.class` bytecode        | `.onnx` model file       |
| JVM (Java VM)            | ONNX Runtime             |
| Write once, run anywhere | Train once, run anywhere |

### **Example platforms with their “JVM” for ONNX:**

- **Windows GPU** -> ONNX Runtime + CUDA
- **macOS** -> ONNX Runtime + CoreML
- **Android** -> ONNX Runtime + NNAPI
- **Raspberry Pi** -> ONNX Runtime (CPU)
- **NVIDIA Jetson** -> ONNX Runtime + TensorRT

### **ONNX Structure:**

```
[ONNX Model Directory]
    |
    +-- tokenizer.json (tokenizer config)
    +-- vocab.txt (vocabulary file)
    |     |
    |     +-- token_id -> token_string mapping
    |     +-- e.g., 0: "[PAD]", 1: "[UNK]", 2: "the", ...
    |
    +-- config.json (model metadata)
    |
    +-- model.onnx (or model_quantized.onnx)
          |
          +-- Graph definition
          +-- Operators
          +-- Weights
```

## **Model Format -> Runner**

- **HF model** (PyTorch) -> `vLLM`, `sentence-transformers`, `transformers` library, PyTorch directly
- **GGUF model** -> `llama.cpp` (and wrappers like LLamaSharp, llama-cpp-python)
- **ONNX model** -> `ONNX Runtime` (and compatible engines like TensorRT, DirectML)

```
[HuggingFace Model]
   +- vLLM (GPU-optimized serving)
   +- sentence-transformers (embeddings)
   +- transformers library (general PyTorch inference)

[GGUF Model]
   +- llama.cpp (CPU-first, C++ inference)

[ONNX Model]
   +- ONNX Runtime (cross-platform, production)
```

## Complete Pipeline Example

```
[User Query: "Hello world"]
    |
    v
[Tokenizer]
    |
    +-- Load vocab.txt (ONNX) or embedded vocab (GGUF)
    +-- Convert: "Hello world" -> [15496, 1879]
    |
    v
[Model Selection]
    |
    +--PyTorch Path-->
    |   |
    |   [Load .safetensors]
    |       |
    |       v
    |   [PyTorch Model] --> CUDA tensors
    |       |
    |       v
    |   [Inference on GPU]
    |
    +--GGUF Path-->
    |   |
    |   [Load .gguf file]
    |       |
    |       v
    |   [llama.cpp inference engine]
    |       |
    |       +-- Memory-map GGUF file
    |       +-- Offload N layers to GPU (via -ngl or GpuLayerCount)
    |       +-- Execute remaining layers on CPU
    |       |
    |       v
    |   [LLamaSharp C# wrapper] (if using .NET)
    |       |
    |       v
    |   [Inference on CPU+GPU hybrid]
    |
    +--ONNX Path-->
    |   |
    |   [Load .onnx file]
    |       |
    |       v
    |   [ONNX Runtime] --> CUDA Execution Provider
    |       |
    |       v
    |   [Inference on GPU]
    |
    v
[Output: embeddings or generated text]
```

## Summary Table

| Category        | Component       | Purpose                          | Related To                      |
|-----------------|-----------------|----------------------------------|---------------------------------|
| **Model Type**  | **HuggingFace** | Original trained model           | PyTorch weights, full ecosystem |
|                 | **GGUF**        | Efficient CPU/GPU inference      | llama.cpp format specification  |
|                 | **ONNX**        | Cross-platform inference         | ONNX Runtime, multiple backends |
| **HuggingFace** | **PyTorch**     | Training and inference framework | HuggingFace native format       |
|                 | **vLLM**        | High-performance serving         | PyTorch models, CUDA            |
| **GGUF**        | **llama.cpp**   | C++ inference engine             | GGUF creator, CPU-optimized     |
|                 | **LLamaSharp**  | C# inference library             | Wraps llama.cpp for .NET        |
| **Tokenizer**   | **Tokenizer**   | Text <--> Token conversion       | All formats need it             |
|                 | **vocab.txt**   | Token ID mapping                 | Tokenization process            |
| **CUDA**        | **CUDA**        | GPU acceleration                 | All frameworks can use it       |
