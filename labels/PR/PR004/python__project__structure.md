# Project Structure - When Docker is Used

```
project/
|-- .env                           # Has envvars - Secrets
|-- scripts/                       # Encapsulates cli args
|       |-- run_data_processor.sh  # Runs main.py with py_cli_args
|       +-- run_project.sh         # Runs docker compose up with docker_cli_args
|
|-- Dockerfile_x
|-- docker-compose-dev-x.yml       # uses Dockerfile_x
|-- docker-compose-x.yml           # uses image created using Dockerfile_x
|
|-- Dockerfile_y
|-- docker-compose-dev-y.yml       # uses Dockerfile_y
|-- docker-compose-y.yml           # uses image created using Dockerfile_y
|
|-- docker_build/                  # Files to be built into docker
|       |-- dockerfile_x/          # lower case to match dockerfile name
|       |   |-- requirements.txt
|       |   +-- entrypoint.sh
|       +-- dockerfile_y/          # lower case to match dockerfile name
|           |-- requirements.txt
|           +-- entrypoint.sh
|
|-- runners/                        # Parameterized runner scripts (numbered for guaranteed order)
|   |-- 01_dev_workflows/           # Multi-step local development workflows (no Docker)
|   |   +-- run_pipeline.sh         # 
|   |
|   |-- 02_docker_dev/              # Docker development workflows
|   |   |-- run_docker-compose-dev-x.sh
|   |   +-- run_docker-compose-dev-y.sh
|   |
|   |-- 03_docker_build/            # Docker image build and publish scripts
|   |   |-- build__x-image.sh       # Build Dockerfile_x image
|   |   |-- publish__x-image.sh     # Publish Dockerfile_x image to DockerHub
|   |   |-- build__y-image.sh       # Build Dockerfile_y image
|   |   +-- publish__y-image.sh     # Publish Dockerfile_y image to DockerHub
|   |
|   |-- 04_docker_prod/             # Docker production workflows (use published images)
|   |   |-- run_docker-compose-x.sh
|   |   +-- run_docker-compose-y.sh
|   |
|   +-- 05_docker_workflows/        # Complete end-to-end Docker workflows
|       +-- run_workflow.sh
|
|-- src/
|   |-- task__011__topic1/          # Specific module
|   |   |-- main.py                 # Entry point
|   |   +-- py_cli_args.py          # Includes all params needed for main.py
|   |
|   |-- task__012__topic2/          # Specific module
|   |   |-- main.py                 # Entry point
|   |   +-- py_cli_args.py          # Includes all params needed for main.py
|   |
|   +-- shared_utils/
|       +-- env_var_defaults.py     # Supplied by .env, docker-compose.yml - has EVERY param
|
+-- scripts_sh/                     # Individual step scripts (used by Docker + dev testing)
    |-- 011__topic1.sh              # runs task__011__topic1/main.py with cli_args
    +-- 012__topic2.sh              # runs task__012__topic2/main.py with cli_args
```