# Claude Code + Ollama: Free Local AI Agent

## Contents

1. [What This Is](#what-this-is)
2. [Architecture](#architecture)
3. [Setup](#setup)
4. [Web Tools Workaround](#web-tools-workaround)
5. [Capability Test Results](#capability-test-results)
6. [What You Get](#what-you-get)
7. [Limitations](#limitations)

---

## What This Is

- Claude Code CLI = agentic framework (file ops, shell, parallel agents, tool calling)
- Ollama = local model server (qwen3.5 9B, free, runs on your GPU)
- Combined = free local AI agent with full Claude Code capabilities

```text
+------------------+          +------------------+
|  Claude Code CLI |  <---->  |  Ollama Server   |
|  (your machine)  |   HTTP   |  (Docker, GPU)   |
|                  |          |                  |
|  - file ops      |          |  - qwen3.5 9B    |
|  - shell/bash    |          |  - 64K context   |
|  - parallel      |          |  - 6.6 GB VRAM   |
|    agents        |          |                  |
+------------------+          +------------------+
```

The model is just a backend. Claude Code does all the heavy lifting.

---

## Architecture

```text
docker-images/
|-- ollama-qwen3pt5_9b/           <-- model server (standard ollama)
|   |-- docker-compose.yml
|   |-- stop_clean_start.sh
|   +-- test_models.sh
|
+-- ollama-claude-code/            <-- client config
    |-- claude-qwen3pt5_9b.sh      <-- wrapper script (entry point)
    |-- CLAUDE.md                  <-- rules for the local model
    |-- .claude/skills/tool__web/  <-- web search + fetch
    +-- _docs/                     <-- verification results
```

Separation: model server knows nothing about Claude Code. Client config knows nothing about Docker.

---

## Setup

### Step 1: Start the model server

```text
cd ollama-qwen3pt5_9b/
./stop_clean_start.sh          <-- pulls ollama 0.20.3, downloads qwen3.5 (~30 min first time)
./test_models.sh               <-- verify with curl
```

qwen3.5 9B (q4_K_M)

- q4 — 4-bit quantization (reduces model size from full 16-bit)
- K — k-quant method (smarter quantization that allocates more bits to important layers)
- M — medium quality tier (between S/small and L/large)

So q4_K_M = 4-bit quantization, k-quant method, medium quality. It's Ollama's default for qwen3.5 — a good balance of size (6.6 GB) vs quality. The full 16-bit model would be ~18 GB

### Step 2: Run Claude Code against it

```text
cd ollama-claude-code/
./claude-qwen3pt5_9b.sh                      <-- interactive mode
./claude-qwen3pt5_9b.sh -p "say hello"       <-- headless mode
```

### What the wrapper does

```bash
ANTHROPIC_AUTH_TOKEN=ollama
ANTHROPIC_BASE_URL=http://localhost:40221
ANTHROPIC_API_KEY=""
claude --model qwen3.5 "$@"
```

Three env vars redirect Claude Code from Anthropic's servers to your local Ollama.

---

## Web Tools Workaround

Built-in WebSearch and WebFetch fail — Claude Code tries to delegate to `claude-haiku` which doesn't exist on Ollama.

### Solution: shell-based skill

```text
+-------------------+     +---------------------+
| tool__web skill   |     | Built-in web        |
|                   |     | (broken on Ollama)  |
| web_search.sh     |     |                     |
|   --> ddgr        |     | WebSearch --> haiku |
|                   |     |   --> FAIL          |
| web_fetch.sh      |     |                     |
|   --> curl        |     | WebFetch --> haiku  |
|   --> text_cleaner|     |   --> FAIL          |
+-------------------+     +---------------------+
```

| Tool       | How                        | Dependency         |
|------------|----------------------------|--------------------|
| Web search | `ddgr` (DuckDuckGo CLI)    | `apt install ddgr` |
| Web fetch  | `curl` + `text_cleaner.py` | built-in           |

### text_cleaner.py

- Strips HTML tags, CSS, JavaScript
- Removes duplicate paragraphs and sentences
- Removes repeated navigation/footer phrases
- 49K chars raw HTML --> 2K chars clean text (96% reduction)

### CLAUDE.md tells the model what to do

```text
NEVER use built-in WebSearch or WebFetch tools.
For web search: .claude/skills/tool__web/scripts/web_search.sh "query"
For web fetch: .claude/skills/tool__web/scripts/web_fetch.sh "url"
```

Explicit commands. A 9B model won't follow "read the skill file" indirection reliably.

---

## Capability Test Results

### Basic (12 tests)

| Capability             | Works? |
|------------------------|--------|
| File read              | Y      |
| File glob              | Y      |
| File grep              | Y      |
| File write             | Y      |
| File edit              | Y      |
| Shell command          | Y      |
| Web search (via skill) | Y      |
| Web fetch (via skill)  | Y      |
| Parallel agents        | Y      |
| MCP server             | -      |
| Python coding          | Y      |
| Shell scripting        | Y      |

### Agentic (6 tests)

| Test                  | Works? | What it did                                                             |
|-----------------------|--------|-------------------------------------------------------------------------|
| Multi-step chaining   | Y      | DuckDB JOIN across 4 tables with differently-named keys, export to JSON |
| Large output handling | Y      | Recursively counted lines per file type                                 |
| Instruction following | Y      | Reformatted JSON to markdown with exact header structure                |
| Error recovery        | Y      | Created missing file, re-read to confirm                                |
| Code correctness      | Y      | Calculated average headcount from DuckDB                                |
| Complex editing       | Y      | Edited JSON config + Python file, ran to verify                         |

**12/12 basic + 6/6 agentic = 18/18 passing**

---

## What You Get

```text
Anthropic Claude Code              Local Claude Code
-------------------                -----------------
~$0.10-0.50 per session    -->     Free
Best-in-class quality      -->     Good enough for structured tasks
Built-in web tools         -->     Shell-based web tools
Always online              -->     Runs offline (except web)
```

### Use cases unlocked by zero cost

- Batch processing session logs (pyramid compaction)
- Bulk transcript processing
- Speculative analysis ("just try it")
- Any structured extractive task at scale

---

## Limitations

| Limitation              | Detail                                                             |
|-------------------------|--------------------------------------------------------------------|
| No built-in web tools   | Workaround via `tool__web` skill                                   |
| 64K context window      | Fine for `claude -p` single-shot; tight for long conversations     |
| Quality gap             | More verbose, no ASCII diagrams, includes filler content           |
| Hallucinated tool calls | Model sometimes claims "file written" without executing write tool |
| RTX 5090 required       | 24 GB VRAM for 9B model + 64K context (~16.6 GB total)             |

### Quality comparison (transcript conversion)

| Aspect         | Anthropic        | qwen3.5 9B                  |
|----------------|------------------|-----------------------------|
| Structure      | Tighter, focused | More sections, some bloat   |
| ASCII diagrams | Yes              | No — uses tables            |
| Prose          | Minimal          | More verbose                |
| Accuracy       | Faithful         | Faithful, no hallucinations |
| Filler         | Omitted          | Included                    |
