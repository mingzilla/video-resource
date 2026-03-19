import json
import logging
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from shared_utils.external.env_var.env_var_reader import EnvVarReader

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Config:
    def __init__(self):
        EnvVarReader.load_dotenv()
        self.is_prod: bool = EnvVarReader.is_prod()

        config_root = EnvVarReader.get_str('CONFIG_ROOT', 'scripts_sh/ex_002__register_ollama')
        config_file = EnvVarReader.get_str('CONFIG_FILE', 'run.json')

        with open(os.path.join(config_root, config_file)) as f:
            data = json.load(f)

        self.gguf_dir: str = data['gguf_dir']
        self.ollama_model_name: str = data['ollama_model_name']
        self.ollama_docker_container: str = data['ollama_docker_container']
        self.system_prompt: str = data['system_prompt']


def find_gguf_file(gguf_dir: str) -> Path:
    matches = list(Path(gguf_dir).glob("*.gguf"))
    if not matches:
        raise FileNotFoundError(f"No .gguf file found in {gguf_dir}")
    if len(matches) > 1:
        raise ValueError(f"Multiple .gguf files found in {gguf_dir}: {matches} — set one explicitly")
    return matches[0]


def run(cmd: list[str]):
    logger.info(f"$ {' '.join(cmd)}")
    subprocess.run(cmd, check=True)


def main():
    config = Config()

    docker = shutil.which("docker")
    if not docker:
        raise FileNotFoundError("docker not found in PATH")

    gguf_path = find_gguf_file(config.gguf_dir).resolve()
    logger.info(f"Found GGUF: {gguf_path}")

    # Copy GGUF into container
    container_gguf = f"/tmp/{gguf_path.name}"
    run([docker, "cp", str(gguf_path), f"{config.ollama_docker_container}:{container_gguf}"])

    # Write Modelfile to a temp file on host, copy into container, then register
    with tempfile.NamedTemporaryFile(mode='w', suffix='_Modelfile', delete=False) as f:
        f.write(f"FROM {container_gguf}\n")
        f.write(f'SYSTEM "{config.system_prompt}"\n')
        temp_modelfile = f.name

    try:
        run([docker, "cp", temp_modelfile, f"{config.ollama_docker_container}:/tmp/Modelfile"])
        run([docker, "exec", config.ollama_docker_container, "ollama", "create", config.ollama_model_name, "-f", "/tmp/Modelfile"])
    finally:
        os.unlink(temp_modelfile)

    logger.info(f"Done. Model '{config.ollama_model_name}' is now available in ollama.")
    logger.info(f"Test with: docker exec {config.ollama_docker_container} ollama run {config.ollama_model_name}")
    return 0


if __name__ == "__main__":
    exit(main())
