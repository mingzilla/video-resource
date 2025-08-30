from abc import ABC, abstractmethod
from typing import List, Optional

from github_mingzilla.llm_mcp.models import ApiChatMessage, DomainMcpTool, LlmResponse


class AbstractLlmClient(ABC):
    @abstractmethod
    async def chat_completion(self, messages: List[ApiChatMessage], model: Optional[str], mcp_tools: Optional[List[DomainMcpTool]]) -> LlmResponse:
        pass

    @abstractmethod
    async def test_connection(self) -> bool:
        pass
