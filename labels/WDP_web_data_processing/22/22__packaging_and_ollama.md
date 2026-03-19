# Packaging and Ollama Registration

- End-to-End Flow
- What the Outputs Are
- Model Naming Convention
- Ollama: Docker-Based, No Local Install
- System Dependencies
- Bugs and Fixes Encountered

Related scripts: `scripts_sh/ex_001__train` (GGUF export) · `scripts_sh/ex_002__register_ollama`

---

## End-to-End Flow

```
ex_001__train
  └─ trains model
  └─ saves lora_adapter/          ← weight deltas only, for future retraining
  └─ saves gguf_gguf/             ← merged + quantised, ready for deployment
        └─ *.Q4_K_M.gguf

ex_002__register_ollama
  └─ docker cp  *.gguf → ollama container:/tmp/
  └─ docker cp  Modelfile → ollama container:/tmp/
  └─ docker exec ollama create company-extractor:llama3.2-3b-v01
```

---

## What the Outputs Are

| Output       | Location                                     | Purpose                                                 |
|--------------|----------------------------------------------|---------------------------------------------------------|
| LoRA adapter | `_output/ex_001__train/lora_adapter/`        | Small weight deltas (~24M params). Keep for retraining. |
| GGUF         | `_output/ex_001__train/gguf_gguf/`           | Merged full model, quantised. Used for deployment.      |
| Modelfile    | Written to `/tmp/Modelfile` inside container | Tells ollama where the GGUF is + the system prompt      |

### Why GGUF

GGUF is the format used by llama.cpp and ollama. It packages the full model weights in a single file with quantisation applied. Once registered, ollama treats it identically to any other model (e.g. `qwen2.5:32b`).

### Quantisation: Q4_K_M

```
Q4_K_M  ← chosen
  4-bit weights, K-quant method, medium variant
  good balance: ~2GB file, minimal quality loss vs full precision
```

---

## Model Naming Convention

Ollama uses `name:tag` format — name is the *what*, tag is the *which variant*:

```
company-extractor:llama3.2-3b-v01
│                 │        │   │
│                 │        │   └─ version, increment as training improves
│                 │        └─ parameter count
│                 └─ base model fine-tuned from
└─ task name
```

Future models naturally fit the same pattern:

```
company-extractor:qwen2.5-3b-v01
company-extractor:llama3.2-3b-v02   ← same base, better training data
```

Multiple versions can be registered simultaneously in ollama for comparison.

---

## Ollama: Docker-Based, No Local Install

ollama runs in Docker — nothing is installed on the host machine. Registration uses standard Docker tooling:

```
docker cp  <gguf>     ollama-test:/tmp/<model>.gguf
docker cp  <Modelfile> ollama-test:/tmp/Modelfile
docker exec ollama-test  ollama create  company-extractor:llama3.2-3b-v01  -f /tmp/Modelfile
```

Config in `run.json`:

```json
"ollama_docker_container": "ollama-test"
```

Change the container name here if the target container changes — no code changes needed.

To verify registration:

```bash
docker exec ollama-test ollama list
```

To test (must pass a prompt — `ollama run` without a prompt exits immediately in non-interactive terminals):

```bash
docker exec ollama-test ollama run company-extractor:llama3.2-3b-v01 "some webtext here"
```

---

## System Dependencies

These must be installed before `uv sync` / first run, as they are needed to build native extensions (bitsandbytes, llama.cpp internals used by unsloth):

```bash
sudo apt-get install -y gcc g++
sudo apt-get install -y libssl-dev libcurl4-openssl-dev cmake
```

| Package                              | Why                                                                    |
|--------------------------------------|------------------------------------------------------------------------|
| `gcc`, `g++`                         | C/C++ compilers for building native Python extensions                  |
| `libssl-dev`, `libcurl4-openssl-dev` | SSL/HTTP libs needed by HuggingFace download internals                 |
| `cmake`                              | Build system used by llama.cpp (invoked by unsloth during GGUF export) |

---

## Bugs and Fixes Encountered

### 1. unsloth must be imported first

```python
# Wrong — triggers UserWarning and loses optimisations
from trl import SFTTrainer
from unsloth import FastLanguageModel

# Correct
from unsloth import FastLanguageModel  # must be first import
from trl import SFTTrainer
```

### 2. SFTConfig parameter rename

```python
# Wrong — raises TypeError in trl >= 0.15
SFTConfig(max_seq_length=4096)

# Correct
SFTConfig(max_length=4096)
```

### 3. unsloth appends `_gguf` suffix to output directory

When calling `model.save_pretrained_gguf("gguf", ...)`, unsloth creates `gguf_gguf/` not `gguf/`.
Workaround: name the output directory `gguf_export` so the result is `gguf_export_gguf/` — predictable and clear.

### 4. Modelfile shell escaping inside docker exec

Initial approach used `printf` + Python `repr()` to write the Modelfile inside the container via `sh -c`. This produced:

- literal `\n` instead of real newlines
- broken shell quoting

Fix: write the Modelfile to a host temp file first, then `docker cp` it into the container. No shell involved.

```text
with tempfile.NamedTemporaryFile(mode='w', suffix='_Modelfile', delete=False) as f:
    f.write(f"FROM {container_gguf}\n")
    f.write(f'SYSTEM "{config.system_prompt}"\n')
    temp_modelfile = f.name

docker cp temp_modelfile → container:/tmp/Modelfile
docker exec container ollama create <name> -f /tmp/Modelfile
```
