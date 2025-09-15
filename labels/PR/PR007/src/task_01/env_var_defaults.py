from typing import List
from .env_var_reader import EnvVarReader


class EnvVarDefaults:
    def __init__(self):
        EnvVarReader.load_dotenv()

        # ---------------------------------------
        # Configure Model using these 4 variables
        self.embedding_url: str = EnvVarReader.get_str_by_env('SCHEMA_EMBEDDING_URL', 'http://all-minilm-embeddings:8000/v1/embeddings', 'http://localhost:30101/v1/embeddings')
        self.embedding_health_url: str = EnvVarReader.get_str_by_env('SCHEMA_EMBEDDING_HEALTH_URL', 'http://all-minilm-embeddings:8000/health', 'http://localhost:30101/health')
        self.embedding_model: str = 'all-MiniLM-L6-v2'
        self.vector_dimension: int = 384
        # ---------------------------------------

        # Web API Configuration for Step 6
        self.api_port: int = EnvVarReader.get_int_by_env('SCHEMA_API_PORT', 41100, 31100)
        EnvVarReader.number_range('SCHEMA_API_PORT', self.api_port, 1, 65535)
