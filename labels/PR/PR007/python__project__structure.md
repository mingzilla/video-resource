# Project Structure

This document outlines the standard directory structure for Python projects, integrating a multi-stage Docker workflow.

```
<project-root>/
|-- .env                         # For SECRETS ONLY. Not for configuration.
|
|-- docker-compose.stage1-prepare-data.yml       # Stage 1: Prepares data. Uses 4xxxx ports.
|-- docker-compose.stage2-build-data-image.yml   # Stage 2: Builds data image. Uses 4xxxx ports.
|-- docker-compose.stage3-build-engine-image.yml # Stage 3: Builds engine image. Uses 4xxxx ports.
|-- docker-compose.dev.yml                       # For local development & testing. Uses 3xxxx ports.
|-- docker-compose.prod.yml                      # For production deployment. Uses 4xxxx ports.
|
|-- Dockerfile_stage1_prepare
|-- Dockerfile_stage2_data
|-- Dockerfile_stage3_engine
|
|-- docker_build/                # Files to be built into docker
|   |-- Dockerfile_stage1/       # For Dockerfile stage1, cannot mirror name, it causes search confusion because Dockerfile does not have file extension
|   |-- Dockerfile_stage2/       # For Dockerfile stage2
|   +-- Dockerfile_stage3/       # For Dockerfile stage3
|
|-- runners/                     # Optional: Scripts for orchestrating complex workflows
|   |-- 01_prepare-data/         # Scripts to run Stage 1 with specific configurations.
|   |-- 02_docker-build/         # Scripts to run Stage 2 & 3 builds.
|   +-- 03_workflow/             # Scripts to run an end-to-end process.
|
|-- src/
|   |-- task__011__topic1/          # Specific module for a "step"
|   |   |-- main.py                 # Entry point
|   |   +-- py_args.py              # Defines env vars needed for this step
|   |
|   |-- task__012__topic2/          # Specific module for a "step"
|   |   |-- main.py                 # Entry point
|   |   +-- py_args.py              # Defines env vars needed for this step
|   |
|   +-- shared_utils/
|       +-- env_var_defaults.py     # Defines ALL default env vars for the application - Use 4xxxx ports
|
+-- scripts_sh/                     # Individual step scripts - DEV: use 3xxxx ports when directly executed, PROD: docker*.yml file use 4xxxx ports to override 3xxxx ports
    |-- 011__topic1.sh              # runs task__011__topic1/main.py
    +-- 012__topic2.sh              # runs task__012__topic2/main.py
```

## Port Allocation

Overriding Order:
- docker-compose.yml overrides `scripts_sh/*.sh`
- `scripts_sh/*.sh` overrides `env_var_defaults.py`

Use 4xxxx (PROD) or 3xxxx (DEV):
- `env_var_defaults.py` - Use `EnvVarReader.get_int_by_env('XXX_PORT', 4xxxx, 3xxxx)` - PROD: 4xxxx, DEV: 3xxxx
- `scripts_sh/*.sh` - Add `export RUNTIME_ENV="${RUNTIME_ENV:-DEV}"` - used by `EnvVarReader`, so that 3xxxx is used unless overridden
- `docker-compose.*.yml` files, except `docker-compose.dev.yml` - `environment: -RUNTIME_ENV=PROD` - overrides `scripts_sh/*.sh`
- `docker-compose.dev.yml` use 3xxxx ports - defines stateful services (e.g. databases with data) used in dev. this file does not have stateless services (e.g. llm models with 3xxxx ports)
  - run `docker container ls | grep :30` to verify stateless services
