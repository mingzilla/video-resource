# Project Structure

## Dockerfile Conventions

| Conventions            | Notes                                              | Problems                                               |
|------------------------|----------------------------------------------------|--------------------------------------------------------|
| Start with uppercase D | Tools use this pattern, don't start with d         | File name mixed case                                   |
| No file extension      |                                                    | If using same folder name, cannot differentiate in cli |
| Use Dockerfile.purpose | Use `.` when you have multiple for different usage | `.exe`, `.web` - confusion                             |

## Naming Suggestions

Typical Requirement: 1 .yml file, 1 Dockerfile, 1 resource directory

- yml: docker-compose.stageN-name.yml ----- with stageN for alphabetical display
- Dockerfile: Dockerfile_stageN_name ------ with stageN for alphabetical display 
- Folder: docker_build/Dockerfile_stageN -- avoid 100% identical name as Dockerfile

## Structure

```
<project-root>/
|-- .env                         # For SECRETS ONLY. Not for configuration.
|
|-- Dockerfile_stage1_prepare
|-- Dockerfile_stage2_data
|-- Dockerfile_stage3_engine
|
|-- docker-compose.stage1-prepare-data.yml       # Stage 1: Prepares data. Uses 4xxxx ports.
|-- docker-compose.stage2-build-data-image.yml   # Stage 2: Builds data image. Uses 4xxxx ports.
|-- docker-compose.stage3-build-engine-image.yml # Stage 3: Builds engine image. Uses 4xxxx ports.
|-- docker-compose.dev.yml                       # For local development & testing. Uses 3xxxx ports.
|-- docker-compose.prod.yml                      # For production deployment. Uses 4xxxx ports.
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
|       +-- env_var_defaults.py     # Defines ALL default env vars for the application.
|
+-- scripts_sh/                     # Individual step scripts (used by Docker + dev testing)
    |-- 011__topic1.sh              # runs task__011__topic1/main.py
    +-- 012__topic2.sh              # runs task__012__topic2/main.py
```
