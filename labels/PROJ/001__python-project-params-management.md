# Python Project Config Parameter Management Pattern

```text
Config Parameter Management
|-- 1. Problem Analysis
|-- 2. Execution Patterns Analysis
|-- 3. Config Parameter Architecture - Comprehensive Guide
|-- 4. Implementation Pattern - Code - Config Parameters
|-- 5. Implementation Pattern - Zero-Config Docker Orchestration
```

**When to use this solution** - whenever implementing code that executes a Python program through:

- Shell scripts (.sh files) that call `python main.py`
- Docker containers running Python programs
- Direct CLI execution of Python programs
- Any runner/launcher mechanism for Python applications

## 1. Problem Analysis

### 1.1. Simplified Execution Patterns

| Pattern              | Flow                                                        |
|----------------------|-------------------------------------------------------------|
| Docker/Orchestration | `sh_script -> docker-compose -> container -> python_script` |
| Direct Execution     | `sh_script -> python_script`                                |

### 1.2. Ways to Supply Config Parameters to a System (2 Ways)

| Type                       | Examples                                     |
|----------------------------|----------------------------------------------|
| **Command Line Arguments** | `--input-file data.json`, `--batch-size 100` |
| **Environment Variables**  | `LLM_URL`, `EMBEDDING_URL`, `OPENAI_API_KEY` |

### 1.3. Where Parameter Values Come From (6 Sources)

| Source                  | Scope | Type     | Method                          | Use Case                              |
|-------------------------|-------|----------|---------------------------------|---------------------------------------|
| **Command Line Input**  | cli   | param    | `./run_script.sh --param value` | User overrides via shell scripts      |
| **Script Content**      | .sh   | hardcode | `BATCH_SIZE=100`                | Direct execution, overrides           |
| **Docker Environment**  | .yml  | envvar   | `environment:` sections         | Container orchestration               |
| **`.env` Files**        | .env  | envvar   | `OPENAI_API_KEY=XXX`            | Local development, secrets            |
| **Hard Coded Defaults** | .py   | hardcode | `os.getenv("VAR", "default")`   | Fallback values in Python             |
| **File Reading**        | .*    | files    | `json.load('config.json')`      | Settings file - read by .sh, .py, ... |

### 1.4. Common Inconsistencies

| Problem                                                   | Description                                                       | Examples                                                                                                                                                                                |
|-----------------------------------------------------------|-------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Inconsistent ways to supply parameter**                 | Same parameter accessible via different mechanisms across scripts | Script A: `sys.argv` parsing<br/>Script B: `os.getenv()` only<br/>Script C: hardcoded values                                                                                            |
| **Inconsistent ways to provide default values**           | Defaults scattered across multiple locations without coordination | `argparse` defaults: `default="http://localhost:8015"`<br/>`EnvVarDefaults`: `embedding_url="http://localhost:8015"`<br/>`docker-compose.yml`: `EMBEDDING_URL: "http://localhost:8015"` |
| **Parameter conflicts - Unclear hierarchical overriding** | No defined precedence chain, unpredictable value resolution       | `sh_cli_args`: `--llm-url http://custom:8080`<br/>`docker_cli_args`: `LLM_URL=http://localhost:8080`<br/>`EnvVarDefaults`: fallback<br/>→ Which wins? Behavior unpredictable            |
| **Parameter conflicts - Duplication of maintenance**      | Same default defined in multiple places, version drift inevitable | Update `embedding_url` requires finding: `docker-compose.yml`, `script_a.py`, `script_b.py`, `env_var_defaults.py`<br/>→ One inevitably gets missed and becomes stale                   |
| **Multiple variables for same concept**                   | Different variable names for same concept due to organic growth   | `EMBEDDING_URL`, `EMBED_URL`, `NOMIC_URL` all pointing to same embedding service<br/>→ Configuration becomes confusing and error-prone                                                  |

### 1.5. Core Problems

| Problem                     | Description                                               |
|-----------------------------|-----------------------------------------------------------|
| **Variable Traceability**   | Hard to track down `where a value is coming from`         |
| **Code Side Effects**       | Variables become code `side effects`                      |
| **Random Injection Points** | `Random` entry point to `inject` a variable into the code |
| **Precedence Ambiguity**    | No clear rules for `which source wins`                    |
| **Maintenance Burden**      | Duplicate variables causing `conflicts` or `out of date`  |

## 2. Execution Patterns Analysis

### 2.1. Execution Patterns

| Pattern                    | Flow                                                                            | Use Case                                    |
|----------------------------|---------------------------------------------------------------------------------|---------------------------------------------|
| **Zero-Config Production** | `(no params)        docker-compose -> envvars -> py_cli_args -> python scripts` | prod - may run multiple python scripts      |
| **Customized Production**  | `docker_cli_args -> docker-compose -> envvars -> py_cli_args -> python scripts` | prod - docker compose up with customisation |
| **Single Script**          | `sh_cli_args +  envvar ------------------------> py_cli_args -> python script`  | dev/debug - run one python script           |

### 2.2. Module Structure Example

```
project/
|-- scripts/                       # Encapsulates cli args
|       |-- run_data_processor.sh  # Runs main.py with py_cli_args
|       +-- run_project.sh         # Runs docker compose up with docker_cli_args
|
|-- Dockerfile
|-- docker-compose.yml             # Has envvars - config
|-- .env                           # Has envvars - Secrets
|
|-- docker_build/                  # Files to be built into docker
|       +-- entrypoint.sh          # Runs main.py with py_cli_args
|
+-- src/
    |-- data_processor/            # Specific module
    |   |-- main.py                # Entry point
    |   +-- py_cli_args.py         # Includes all params needed for main.py
    |
    +-- shared_utils/
        +-- env_var_defaults.py    # Supplied by .env, docker-compose.yml - has EVERY param
```

### 2.3. 3 Entry Points to Accept Parameters

**Three distinct entry points**, which accepts params for different execution stages:

| Parameter Type        | Flow                      | Purpose                                   | Example                                                |
|-----------------------|---------------------------|-------------------------------------------|--------------------------------------------------------|
| **`    sh_cli_args`** | CLI → .sh file            | Parameters user provides to shell scripts | `./run_project.sh --embedding-url http://custom.com`   |
| **`docker_cli_args`** | .sh file → docker-compose | Parameters to create container envvars    | `EMBEDDING_URL=http://custom.com docker-compose up -d` |
| **`    py_cli_args`** | .sh file → main.py        | Parameters given to Python to run it      | `python my_script.py arg1 arg2`                        |

## 3. Config Parameter Architecture - Comprehensive Guide

### 3.1. Parameter Flow Diagrams

```text
# PROD Flow (Container Execution)
                          CLI user
                              |
          sh_cli_args --> run_project.sh               # sh_cli_args - for human (ideally avoid) -> create multiple no-cli-args .sh files, which hardcode different sets of docker_cli_args
                              |
      docker_cli_args --> docker-compose.yml           # envvars only - ALL params supplied to downstream can only be envvars
                              |
container environment --> entrypoint.sh
                              |
  (avoid) py_cli_args --> python main.py               # envvars only - for simplicity - DO NOT convert envvars to cmd params
                              |
                   Line 1: envvars = EnvVarDefaults()  # envvars only - P1 Docker > P2 .env > P3 hardcode
                   Line 2: py_cli_args = PyCliArgs.create_from(envvars)

# DEV Flow (Direct Execution)
                  CLI user
                      |
  sh_cli_args --> run_data_processor.sh        # sh_cli_args - for human - avoid -> create multiple no-cli-args .sh files, which hardcode different sets of py_cli_args
                      |
  py_cli_args --> python main.py               # py_cli_args - multiple .sh files with different py_cli_args
                      |
           Line 1: envvars = EnvVarDefaults()  # Priority: py_cli_args > .env > hardcode
           Line 2: py_cli_args = PyCliArgs.create_from(envvars)
```

### 3.2. Config Params Priorities - Conflict Resolution - High Overrides Low

| PROD Layer       | Source                         | Scope | Type     | Why this Priority      | Justification                                                                     | Example                                                             |
|------------------|--------------------------------|-------|----------|------------------------|-----------------------------------------------------------------------------------|---------------------------------------------------------------------|
| **P1 (Highest)** | `sh_cli_args`                  | cli   | params   | Intentionally Supplied | AVOID - Needs human to remember, ideally avoid, use P2 instead                    | `./run.sh --llm-url http://custom.com`                              |
| **P2 (High)**    | `docker_cli_args`              | .sh   | params   | Intentionally Supplied | 1 or many no-cli-args .sh files, which hardcode different sets of docker_cli_args | `MY_VAR=override docker compose up`                                 |
| **P3 (Middle)**  | `docker-compose.yml` hardcoded | .yml  | envvars  | Execution Preference   | Allow Zero Config to run app                                                      | `LLM_URL=${LLM_URL:-http://docker-default:8080}`                    |
| **P4 (Low)**     | `.env`                         | .env  | envvars  | System Config          | Single Source for - secrets                                                       | `OPENAI_API_KEY=xxxxxx`                                             |
| **P5 (Lowest)**  | `EnvVarDefaults` fallback      | .py   | hardcode | Default Values         | Single Source for - default values                                                | `os.getenv("LLM_URL", "http://python-default:11434")`               |
| **N/A**          | `PyCliArgsXXX`                 | N/A   | N/A      | N/A                    | **Must not contain hardcoded defaults.**                                          | `parser.add_argument('--llm-url', default=envvar_defaults.llm_url)` |

| DEV Layer        | Source                    | Scope | Type     | Why this Priority      | Justification                                                                 | Example                                                             |
|------------------|---------------------------|-------|----------|------------------------|-------------------------------------------------------------------------------|---------------------------------------------------------------------|
| **D1 (Highest)** | `sh_cli_args`             | cli   | params   | Intentionally Supplied | AVOID - Needs human to remember, ideally avoid, use D3 instead                | `./run.sh --llm-url http://custom.com`                              |
| **D2 (High)**    | `export VAR=x`            | .sh   | envvars  | Intentionally Supplied |                                                                               | `export VAR=x`                                                      |
| **D3 (High)**    | `py_cli_args`             | .sh   | params   | Intentionally Supplied | 1 or many no-cli-args .sh files, which hardcode different sets of py_cli_args | `python main.py --source-db path`                                   |
| **D4 (Low)**     | `.env`                    | .env  | envvars  | System Config          | Single Source for - secrets                                                   | `OPENAI_API_KEY=xxxxxx`                                             |
| **D5 (Lowest)**  | `EnvVarDefaults` fallback | .py   | hardcode | Default Values         | Single Source for - default values                                            | `os.getenv("LLM_URL", "http://python-default:11434")`               |
| **N/A**          | `PyCliArgsXXX`            | N/A   | N/A      | N/A                    | **Must not contain hardcoded defaults.**                                      | `parser.add_argument('--llm-url', default=envvar_defaults.llm_url)` |

#### 3.2.1. Config Params (docker-compose) Guide - Docker-Compose Variable Patterns - When to Use Which Syntax

- P1 - avoid - use .sh file with docker_cli_args
- P2 - supplied when reusing same docker-compose.yml file
- P3 - enable zero config execution

|   | Pattern                                          | Typical File                      | cli     | docker   | .env    | EnvVarDefaults | Comment                               |
|---|--------------------------------------------------|-----------------------------------|---------|----------|---------|----------------|---------------------------------------|
| 1 | `LLM_URL=${LLM_URL}`                             | docker-compose.yml                | allowed |          | allowed | fallback       | Recommend - Single consistent default |
| 2 | `LLM_URL=${LLM_URL:-http://docker-default:8080}` | docker-compose-special-shared.yml | allowed | override |         | fallback       | Non-default, used by multiple scripts |
| 3 | `LLM_URL=http://fixed-service:8080`              | docker-compose-special-single.yml |         | override |         | fallback       | Non-default, param ties to this value |

- allowed - means it enables overriding
- override - intentionally overrides the default, because this is not the default `docker-compose.yml` file. default file uses default values
- fallback - means we provide default value here
- `LLM_URL=${LLM_URL}` - without doing so, it's not possible for docker_cli_args to be given to entrypoint.sh

#### 3.2.2. Config Params (EnvVarDefaults)

- P4 - only for secrets
- P5 - P1) reads container envvars - overrides .env, P2) reads .env, P3) offer DEFAULTS

`EnvVarDefaults` is the single place that has EVERY SINGLE argument supplied to python

- IN ONE PLACE
    - WHY - PROD mode - no cli args allowed for main.py, hence only envvars are given to main.py
    - BENEFITS - easy to identify `redundant`, `unused`, `inconsistent` parameters
- Rules in this file:
    - Type Conversion - in one place - str -> number, str -> bool
    - Parameter Validation - best place to provide validation because every parameter is here
    - PyCliArgsXXX - Must contain `EVERY parameter` needed by any `PyCliArgsXXX` since PROD containers have no CLI override capability.
- Priorities in this file:
    - Priority 1 - **reads** environment variables (set by docker-compose), overrides .env
    - Priority 2 - **reads** `.env` files (via `os.getenv()`)
    - Priority 3 - provides fallback defaults when environment variables are not set

### 3.3. Config Params Architecture Summary - Cascading Override Principle

1. **EnvVarDefaults**: Has All DEFAULTS and EVERY parameter - Single Source of Truth
2. **Override Rule**: Upstream overrides = upstream has variations ---- Many(upstream) → 1(downstream)
3. **Principle**: Keep values as low level as possible

#### 3.3.1. EnvVarDefaults Override Scenarios

EnvVarDefaults remains the single source of truth, with intentional overrides in these specific cases:

- **D3 Override**: Dev shell scripts (`scripts_sh/*.sh`) hardcode values to create no-CLI-args scripts for specific purposes
- **P3 Override**: Non-default docker-compose files override P5 defaults when using multiple compose files
- **P2 Override**: Non-default shell files provide specific values to docker-compose, overriding P5 via docker environment

## 4. Implementation Pattern - Code - Config Parameters

### 4.1. Implementation Pattern - EnvVarDefaults

```python
# shared_utils/env_var_defaults.py
class EnvVarDefaults:
    def __init__(self):
        load_dotenv(override=False)  # Explicitly avoids overriding if envvar exists - enables P1 Docker > P2 .env
        self.openai_api_key: str = os.getenv("OPENAI_API_KEY", "default-key")  # default value (P3)
```

### 4.2. Implementation Pattern - PyCliArgsXXX

```python
# src/data_processor/py_cli_args.py
class PyCliArgsXXX:
    def __init__(self, args):
        self.llm_url = args.llm_url

    @classmethod
    def create_from(cls, envvars: EnvVarDefaults) -> 'PyCliArgsXXX':
        parser = argparse.ArgumentParser()
        parser.add_argument('--llm-url', default=envvars.llm_url)
        parsed_args = parser.parse_args()
        return cls(parsed_args)
```

### 4.3. Implementation Pattern - main.py

```python
# src/data_processor/main.py
def main():
    from shared_utils.env_var_defaults import EnvVarDefaults
    from .py_cli_args import PyCliArgsXXX
    envvars = EnvVarDefaults()
    params = PyCliArgsXXX.create_from(envvars)
    print(f"LLM URL: {params.llm_url}")
    # ... your business logic here ...


if __name__ == '__main__':
    main()
```

## 5. Implementation Pattern - Zero-Config Docker Orchestration

### 5.1. Release Branch Pattern - support zero-configuration startup:

```bash
# Rule: This must always work for any release branch
git checkout build/2025-08.002
docker-compose up -d
# All services start with working defaults
```

### 5.2. Single vs Multiple Docker-Compose Files

| Strategy           | When to Use                                          | Example                                                  | Trade-offs                                            |
|--------------------|------------------------------------------------------|----------------------------------------------------------|-------------------------------------------------------|
| **Single File**    | Services can be shared with different configurations | `docker-compose.yml` with environment variable overrides | Simpler, but may run unused services                  |
| **Multiple Files** | Services cannot be shared, avoid unused services     | `docker-compose.yml`, `docker-compose.nomic.yml`         | More files to maintain, but cleaner service isolation |
