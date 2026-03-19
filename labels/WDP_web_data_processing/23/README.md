# Running a Fine-Tuned Model with Ollama

## Directory Layout

```
ollama__company_extractor_llama3pt2_3b/
|-- docker-compose.yml
|-- models/               # place .gguf files here (gitignored except .gitkeep)
|   |-- llama-3.2-3b-instruct.Q4_K_M.gguf
|   +-- Modelfile
+-- README.md

[docker] -- [Modelfile] -- [llama-3.2-3b-instruct.Q4_K_M.gguf]
```

## Steps

### 1. Make this file: Modelfile yourself:

```text
FROM /models/llama-3.2-3b-instruct.Q4_K_M.gguf
SYSTEM "Extract company information from the website content in British English."
```

### 2. Copy a trained GGUF and Modelfile into `models/`

```text
llama-3.2-3b-instruct.Q4_K_M.gguf
Modelfile
```

### 3. Start the Ollama container

```bash
# Run Ollama
docker compose up -d

# Register Model
docker exec ollama-test ollama create company-extractor:llama3.2-3b-v01 -f /models/Modelfile
```

### 4. Verify and test

```bash
docker exec ollama-test ollama list
docker exec ollama-test ollama run company-extractor:llama3.2-3b-v01 "some webtext here"
```

## Switching Models

1. Copy the new `.gguf` into `models/`
2. Register it under a new tag (e.g. `company-extractor:llama3.2-3b-v02`)
3. Update any downstream config to point at the new tag

Multiple versions can be registered simultaneously for comparison. To remove an old version:

## Remove Models

```bash
docker exec ollama-test ollama rm company-extractor:llama3.2-3b-v01
```
