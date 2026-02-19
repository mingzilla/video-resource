# vLLM

## Small Models from vLLM

### ✅ Qwen2.5 Models (YES - Fully Supported)

```text
# vLLM supports Qwen2ForCausalLM architecture - These specific models will work:

"Qwen/Qwen2.5-1.5B-Instruct"     # ⭐ BEST CHOICE - 128K context
"Qwen/Qwen2.5-3B-Instruct"       # Better quality - 128K context
"Qwen/Qwen2.5-0.5B-Instruct"     # Fastest - 128K context
"Qwen/Qwen2.5-7B-Instruct"       # Highest quality - 128K context

vLLM Architecture: Qwen2ForCausalLM ✅
```

### ✅ Gemma Models (YES - Fully Supported)

```text
# Gemma 2 (your 8K sweet spot)
"google/gemma-2-2b-it"           # ⭐ 8K context, instruction-tuned
"google/gemma-2-9b-it"           # 8K context (larger, slower)
```

## Model of Choices

| Model                     | GPU Requirement                       | CPU‑only Performance                          |
|---------------------------|---------------------------------------|-----------------------------------------------|
| **Qwen2.5‑1.5B‑Instruct** | 4–6GB VRAM (e.g., GTX 1660, RTX 3060) | Works but slower (≈ same as Ollama quantized) |
| **Gemma‑2‑2B**            | 6–8GB VRAM                            | Works but slower                              |

### Option 1: Qwen2.5-1.5B-Instruct (BEST):

```shell
# Install vLLM
pip install vllm

# Start server (simple!)
python -m vllm.entrypoints.openai.api_server \
  --model Qwen/Qwen2.5-1.5B-Instruct \
  --port 30202 \
  --max-model-len 8192

# Your code works unchanged! Same OpenAI-compatible API
curl http://localhost:30203/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d '{
      "model": "Qwen/Qwen2.5-1.5B-Instruct",
      "messages": [
        {"role": "user", "content": "Your prompt here"}
      ],
      "max_tokens": 100,
      "temperature": 0.7
    }'
```

Why:

- ✅ 128K context (way beyond your 8K need)
- ✅ Smallest, fastest Qwen option
- ✅ Excellent at structured extraction
- 🌍 Multilingual support
- ✅ Same API as Ollama (no code changes!)

Expected speed (with GPU):

- With GPU: 0.1-0.2 sec/item → 2M in 2-4 days
- CPU only: 0.5-1.0 sec/item → similar to current

### Option 2: Gemma-2-2B-IT (If you want exactly 8K)

```shell
python -m vllm.entrypoints.openai.api_server \
  --model google/gemma-2-2b-it \
  --port 30203 \
  --max-model-len 8192

curl http://localhost:30203/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d '{
      "model": "google/gemma-2-2b-it",
      "messages": [
        {"role": "user", "content": "Your prompt here"}
      ],
      "max_tokens": 100,
      "temperature": 0.7
    }'
```

## Docker Containers:

| File             | Model        | Size | Port  | Speed       | Context | Best For                           |
|------------------|--------------|------|-------|-------------|---------|------------------------------------|
| qwen2.5-1.5b.yml | Qwen2.5-1.5B | ~3GB | 30202 | ⚡⚡⚡ Fastest | 128K    | Speed (est. 0.2-0.3s/item)         |
| qwen2.5-3b.yml   | Qwen2.5-3B   | ~6GB | 30202 | ⚡⚡ Fast     | 128K    | Balance (est. 0.4-0.5s/item)       |
| gemma-2-2b.yml   | Gemma-2-2B   | ~5GB | 30203 | ⚡⚡ Fast     | 8K      | Exact 8K need (est. 0.3-0.4s/item) |

```shell
# Run Qwen 1.5B (fastest)
docker compose -f docker-compose.qwen2.5-1.5b.yml up -d

# OR run Qwen 3B (better quality)
docker compose -f docker-compose.qwen2.5-3b.yml up -d

# OR run Gemma 2-2B (exactly 8K context)
docker compose -f docker-compose.gemma-2-2b.yml up -d

# Stop whichever is running
docker compose -f docker-compose.qwen2.5-1.5b.yml down
# or
docker compose -f docker-compose.qwen2.5-3b.yml down
# or
docker compose -f docker-compose.gemma-2-2b.yml down
```

## Verifying if models are available from vllm

Any model on HuggingFace with these architectures will work in vLLM:

1. Go to HuggingFace model page
2. Check "Model Card" → look for architecture name
3. If it matches vLLM's supported list → it works!

Example:

- Model: Qwen/Qwen2.5-1.5B-Instruct
- Architecture: Qwen2ForCausalLM
- vLLM support: ✅ YES (listed in docs)
- Result: Will work!

## Check Context Window:

curl http://localhost:30202/v1/models

```json
{
  "object": "list",
  "data": [
    {
      "id": "Qwen/Qwen2.5-1.5B-Instruct",
      "object": "model",
      "created": 1769200993,
      "owned_by": "vllm",
      "root": "Qwen/Qwen2.5-1.5B-Instruct",
      "parent": null,
      "max_model_len": 8192,
      "permission": [
        {
          "id": "modelperm-9045f8f41ad843c1",
          "object": "model_permission",
          "created": 1769200993,
          "allow_create_engine": false,
          "allow_sampling": true,
          "allow_logprobs": true,
          "allow_search_indices": false,
          "allow_view": true,
          "allow_fine_tuning": false,
          "organization": "*",
          "group": null,
          "is_blocking": false
        }
      ]
    }
  ]
}
```

curl http://localhost:30203/v1/models

```json
{
  "object": "list",
  "data": [
    {
      "id": "google/gemma-2-2b-it",
      "object": "model",
      "created": 1769199629,
      "owned_by": "vllm",
      "root": "google/gemma-2-2b-it",
      "parent": null,
      "max_model_len": 8192,
      "permission": [
        {
          "id": "modelperm-9acd4d1bebad52b5",
          "object": "model_permission",
          "created": 1769199629,
          "allow_create_engine": false,
          "allow_sampling": true,
          "allow_logprobs": true,
          "allow_search_indices": false,
          "allow_view": true,
          "allow_fine_tuning": false,
          "organization": "*",
          "group": null,
          "is_blocking": false
        }
      ]
    }
  ]
}
```