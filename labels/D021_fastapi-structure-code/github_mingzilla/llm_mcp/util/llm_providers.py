from github_mingzilla.llm_mcp.llm_clients.abstract_llm_client import AbstractLlmClient
from github_mingzilla.llm_mcp.llm_clients.llm_ollama_client import LLMOllamaClient
from github_mingzilla.llm_mcp.llm_clients.llm_openai_client import LLMOpenAIClient


class LLMProviders:
    def __init__(self):
        self._provider_dict = {
            "ollama": LLMOllamaClient(),
            "openai": LLMOpenAIClient(),
        }

    def get_by_name(self, provider_name: str) -> AbstractLlmClient:
        return self._provider_dict[provider_name] or LLMOllamaClient()
