# Python Project Cli Args and Env Vars Management Pattern

**When to use this solution** - whenever implementing code that executes a Python program directly or via docker:

```text
Cli Args and Env Vars Management
|-- 1. Problem Analysis
|-- 2. Recommended Solution
|-- 3. Handle Cli Args and Env Vars - Comprehensive Guide
|-- 4. Handle Cli Args and Env Vars - Unified Solution
|-- 5. Implementation Pattern - Code - Cli Args and Env Vars
|-- 6. Implementation Pattern - Zero-Config Docker Orchestration
|-- 7. Additional Info
```

Summary of rules:

| Pattern | Flow                                        | Flow                                         |
|---------|---------------------------------------------|----------------------------------------------|
| PROD    | `project.sh (no args) -> docker-compose ->` | `module_step.sh (override) -> python_script` |
| DEV     | `->`                                        | `module_step.sh (no args) --> python_script` |

- **Avoid cli args** - use envvars for a unified solution; goal: *.sh files can be run without cli args
- **EnvVarsDefaults** - only use one file `EnvVarsDefaults` to encapsulate envvar reading. this file is the single source of all envvars, with default values and validation
    - **envvars priority** - `exiting > .env > hardcoded`, pattern is enforced by `EnvVarReader` (single place to have `os.getenv()`)
- **call flow** - `project.sh (prod only) -> docker (prod only) -> module_step.sh (dev no args) -> python (EnvVarsDefaults)`
    - **module_step.sh** - uses `export SIZE="${SIZE:-100}"` pattern, allows dev without cli arg, and prod upstream overriding
    - **exposes envvars** - when exposing envvars to be overridden: indicates that upstream has multiple files with different values to set this envvar

## 1. Problem Analysis

### 1.1. Ways to Supply Config Parameters to a System (2 Ways)

| Type                       | Examples                                     |
|----------------------------|----------------------------------------------|
| **Command Line Arguments** | `--input-file data.json`, `--batch-size 100` |
| **Environment Variables**  | `LLM_URL`, `EMBEDDING_URL`, `OPENAI_API_KEY` |

### 1.2. Execution Patterns and Concepts

|      | ->                   | pipeline.sh             | -> | docker:  entrypoint.sh   | -> | step_x.sh                       | ->                   | .env        | main.py                    |
|------|----------------------|-------------------------|----|--------------------------|----|---------------------------------|----------------------|-------------|----------------------------|
| PROD | P1 `cli_args_for_sh` | P2 `envvars_for_docker` |    | P3 `envvars_from_docker` |    | `envvars_for_py` (from docker)  | `cli_args_for_py`    | P4 SECRET=x | P5 EnvVarDefaults fallback |
| DEV  | D1 `cli_args_for_sh` |                         |    |                          |    | D2 `envvars_for_py` (hardcoded) | D3 `cli_args_for_py` | D4 SECRET=x | D5 EnvVarDefaults fallback |

### 1.3. Where Parameter Values Come From

| Source                  | Scope | Type     | P  | D  | Flow                           | Example                                              |
|-------------------------|-------|----------|----|----|--------------------------------|------------------------------------------------------|
| `cli_args_for_sh`       | cli   | cli_args | P1 | D1 | CLI → .sh file arguments       | `./run_project.sh --embedding-url http://custom.com` |
| `envvars_for_docker`    | .sh   | envvar   | P2 |    | .sh file → docker-compose      | `export SIZE=10`, `docker-compose up -d`             |
| `envvars_from_docker`   | .yml  | envvar   | P3 |    | docker-compose → entrypoint.sh | `LLM_URL=${LLM_URL}`                                 |
| `envvars_for_py`        | .sh   | envvar   |    | D2 | .sh file → main.py             | `export SIZE=10`, `python my_script.py`              |
| `cli_args_for_py`       | .sh   | cli_args |    | D3 | .sh file → main.py             | `python my_script.py arg1 arg2`                      |
| **`.env` Files**        | .env  | envvar   | P4 | D4 |                                | `OPENAI_API_KEY=XXX`                                 |
| **Hard Coded Defaults** | .py   | hardcode | P5 | D5 |                                | `os.getenv("VAR", "default")`                        |
| **File Reading**        | .*    | files    |    |    | (out of discussion scope)      | `json.load('config.json')`                           |

### 1.4. Common Issues

- Inconsistent ways to: 1) supply parameter, 2) provide default values, 3) inconsistent overriding, 4) redundant, 5) out of date
- For more: refer to end of this doc

## 2. Recommended Solution

### 2.1. Execution Patterns

|      | -> | workflow.sh          | -> | docker:  entrypoint.sh | -> | step_x.sh                                  | -> | .env     | main.py                 |
|------|----|----------------------|----|------------------------|----|--------------------------------------------|----|----------|-------------------------|
| PROD |    | `envvars_for_docker` |    | `envvars_from_docker`  |    | `envvars_for_py` (N/A - ALL from docker)   |    | SECRET=x | EnvVarDefaults fallback |
| DEV  |    | N/A                  |    | N/A                    |    | `envvars_for_py` (override or leave blank) |    | SECRET=x | EnvVarDefaults fallback |

### 2.2. Justification

- Rule R0: overriding order - left > right: Values from the left overrides downstream values (because of the flow of calling)
- Rule R1: step_x.sh - PROD envvars only - in PROD, docker can only supply envvars to downstream, no reason to create `cli_args_for_py` because python can read envvars
- Rule R2: step_x.sh - DEV envvars only - because of R1, for DEV PROD consistency, just use D2 `envvars`, avoid D3 `cli_args`
- Rule R5: step_x.sh - use `VAR="${VAR:-'text'}"` pattern because:
    - PROD - expose - need to expose a variable to be overridden by `envvars_from_docker`
    - DEV - override - 1) override a value to avoid `cli_args_for_sh`, 2) leave blank to use EnvVarDefaults
    - `export VAR=x` - this uses sub-shell, so it does not leak envvars outside the script, it perfectly replaces `cli_args` usage and offers the same result
- Rule R3: *.sh replaces `cli_args` - to avoid remembering `cli_args`, avoid P1 and D1, create multiple scripts to have P2 variations and D2 variations
- Rule R4: ENTRY envvars only - because of R2 and R3, avoid `cli_args` completely, only use `envvars` in the whole solution

### 2.3. Module Structure Example

```
project/
|-- scripts/                       # Encapsulates cli envvars
|       |-- run_data_processor.sh  # Runs main.py with envvars_for_py
|       +-- run_project.sh         # Runs docker compose up with envvars_for_docker
|
|-- Dockerfile
|-- docker-compose.yml             # Has envvars - config
|-- .env                           # Has envvars - Secrets
|
|-- docker_build/                  # Files to be built into docker
|       +-- entrypoint.sh          # Runs main.py with envvars_from_docker
|
+-- src/
    |-- data_processor/            # Specific module
    |   |-- main.py                # Entry point
    |   +-- py_args.py             # PyArgs - Includes all params needed for main.py
    |
    +-- shared_utils/
        +-- env_var_defaults.py    # EnvVarDefaults - Supplied by .env, docker-compose.yml - has EVERY param
```

```text
python main.py
Line 1: envvars = EnvVarDefaults()  # Priority: existing_envvars > .env > hardcode
Line 2: py_args = PyArgsXXX.create_from(envvars) # (avoid - use envvars directly)
```

## 3. Handle Cli Args and Env Vars - Comprehensive Guide

### 3.1. Config Params (docker-compose) Guide - Docker-Compose Variable Patterns - When to Use Which Syntax

|   | Pattern                                          | Typical File                      | cli     | docker   | .env    | EnvVarDefaults | Comment                               |
|---|--------------------------------------------------|-----------------------------------|---------|----------|---------|----------------|---------------------------------------|
| 1 | `LLM_URL=${LLM_URL}`                             | docker-compose.yml                | allowed |          | allowed | fallback       | Recommend - Single consistent default |
| 2 | `LLM_URL=${LLM_URL:-http://docker-default:8080}` | docker-compose-special-shared.yml | allowed | override |         | fallback       | Non-default, used by multiple scripts |
| 3 | `LLM_URL=http://fixed-service:8080`              | docker-compose-special-single.yml |         | override |         | fallback       | Non-default, param ties to this value |

- allowed - means it enables overriding
- override - intentionally overrides the default, because this is not the default `docker-compose.yml` file. default file uses default values
- fallback - means we provide default value here
- `LLM_URL=${LLM_URL}` - without doing so, it's not possible for envvars_for_docker to be given to entrypoint.sh

### 3.2. Config Params (EnvVarDefaults)

`EnvVarDefaults` is the single place that has EVERY SINGLE argument supplied to python

- IN ONE PLACE
    - WHY - PROD mode - no cli args allowed for main.py, hence only envvars are given to main.py
    - BENEFITS - easy to identify `redundant`, `unused`, `inconsistent` parameters
- Rules in this file:
    - Type Conversion - in one place - str -> number, str -> bool
    - Parameter Validation - best place to provide validation because every parameter is here
    - PyArgsXXX - Must contain `EVERY parameter` needed by any `PyArgsXXX` since PROD containers have no CLI override capability.
- Priorities in this file: envvars > .env > default
    - Priority 1 - **reads** environment variables (set by docker-compose), overrides .env
    - Priority 2 - **reads** `.env` files (via `os.getenv()`)
    - Priority 3 - provides fallback defaults when environment variables are not set

## 4. Handle Cli Args and Env Vars - Unified Solution

1. **Cli args**: AVOID `cli_args` completely, use `export VAR=x` sub-shell envvars solution instead
2. **EnvVarDefaults**: Has All DEFAULTS and EVERY parameter - Single Source of Truth
3. **Override Rule**: Upstream overrides = upstream has variations ---- Many(upstream) → 1(downstream)
4. **Principle**: Keep values as low level as possible
5. step_x.sh - use `VAR="${VAR:-'text'}"` pattern because:
    - PROD - expose - need to expose a variable to be overridden by docker
    - DEV - override - 1) override a value to run zero args script, 2) leave blank to use EnvVarDefaults
6. EnvVarDefaults Override Scenarios - EnvVarDefaults remains the single source of truth, with intentional overrides in these specific cases:
    - **D2 Override**: Dev shell scripts (`scripts_sh/*.sh`) hardcode envvar values to create no-CLI-args scripts for specific purposes
    - **P3 Override**: Non-default docker-compose files override P5 defaults when using multiple compose files
    - **P2 Override**: Non-default shell files provide specific values to docker-compose, overriding P5 via docker environment

## 5. Implementation Pattern - Code - Config Parameters

### 5.1. Implementation Pattern - EnvVarDefaults

```python
# shared_utils/env_var_defaults.py
class EnvVarDefaults:
    def __init__(self):
        EnvVarReader.load_dotenv()  # Force Priority: existing envvars > .env
        self.batch_size: int = EnvVarReader.get_int('COMPANY_BATCH_SIZE', '10')  # Force Priority: .env > default
        EnvVarReader.number_min('COMPANY_BATCH_SIZE', self.batch_size, 1)  # Validation
```

### 5.2. Implementation Pattern - PyArgsXXX

```python
# src/data_processor/py_args.py
class PyArgsXXX:
    def __init__(self, envvars: EnvVarDefaults):
        self.llm_url = envvars.llm_url

    @classmethod
    def create_from(cls, envvars: EnvVarDefaults) -> 'PyArgsXXX':
        return cls(envvars)
```

### 5.3. Implementation Pattern - main.py

```python
# src/data_processor/main.py
def main():
    from shared_utils.env_var_defaults import EnvVarDefaults
    from .py_args import PyArgsXXX
    envvars = EnvVarDefaults()
    params = PyArgsXXX.create_from(envvars)
    print(f"LLM URL: {params.llm_url}")
    # ... your business logic here ...


if __name__ == '__main__':
    main()
```

## 6. Implementation Pattern - Zero-Config Docker Orchestration

### 6.1. Release Branch Pattern - support zero-configuration startup:

```bash
# Rule: This must always work for any release branch
git checkout build/2025-08.002
docker-compose up -d
# All services start with working defaults
```

### 6.2. Single vs Multiple Docker-Compose Files

| Strategy           | When to Use                                          | Example                                                  | Trade-offs                                            |
|--------------------|------------------------------------------------------|----------------------------------------------------------|-------------------------------------------------------|
| **Single File**    | Services can be shared with different configurations | `docker-compose.yml` with environment variable overrides | Simpler, but may run unused services                  |
| **Multiple Files** | Services cannot be shared, avoid unused services     | `docker-compose.yml`, `docker-compose.nomic.yml`         | More files to maintain, but cleaner service isolation |

## 7. Common Issues

### 7.1. Common Inconsistencies

| Problem                                                   | Description                                                       | Examples                                                                                                                                                                                |
|-----------------------------------------------------------|-------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Inconsistent ways to supply parameter**                 | Same parameter accessible via different mechanisms across scripts | Script A: `sys.argv` parsing<br/>Script B: `os.getenv()` only<br/>Script C: hardcoded values                                                                                            |
| **Inconsistent ways to provide default values**           | Defaults scattered across multiple locations without coordination | `argparse` defaults: `default="http://localhost:8015"`<br/>`EnvVarDefaults`: `embedding_url="http://localhost:8015"`<br/>`docker-compose.yml`: `EMBEDDING_URL: "http://localhost:8015"` |
| **Parameter conflicts - Unclear hierarchical overriding** | No defined precedence chain, unpredictable value resolution       | `cli_args_for_sh`: `--llm-url http://custom:8080`<br/>`envvars_for_docker`: `LLM_URL=http://localhost:8080`<br/>`EnvVarDefaults`: fallback<br/>→ Which wins? Behavior unpredictable     |
| **Parameter conflicts - Duplication of maintenance**      | Same default defined in multiple places, version drift inevitable | Update `embedding_url` requires finding: `docker-compose.yml`, `script_a.py`, `script_b.py`, `env_var_defaults.py`<br/>→ One inevitably gets missed and becomes stale                   |
| **Multiple variables for same concept**                   | Different variable names for same concept due to organic growth   | `EMBEDDING_URL`, `EMBED_URL`, `NOMIC_URL` all pointing to same embedding service<br/>→ Configuration becomes confusing and error-prone                                                  |

### 7.2. Core Problems

| Problem                     | Description                                               |
|-----------------------------|-----------------------------------------------------------|
| **Variable Traceability**   | Hard to track down `where a value is coming from`         |
| **Code Side Effects**       | Variables become code `side effects`                      |
| **Random Injection Points** | `Random` entry point to `inject` a variable into the code |
| **Precedence Ambiguity**    | No clear rules for `which source wins`                    |
| **Maintenance Burden**      | Duplicate variables causing `conflicts` or `out of date`  |
