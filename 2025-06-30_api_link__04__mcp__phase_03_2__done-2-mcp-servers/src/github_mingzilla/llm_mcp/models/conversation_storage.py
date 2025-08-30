from typing import Dict, List, Optional

from github_mingzilla.llm_mcp.models.chat_models import ChatMessage


class ConversationStorage:
    """In-memory conversation storage for Phase 1 implementation."""

    def __init__(self):
        self._conversations: Dict[str, List[ChatMessage]] = {}

    def get_or_create_conversation(self, session_id: str) -> List[ChatMessage]:
        """Get existing conversation or create new one."""
        if session_id not in self._conversations:
            self._conversations[session_id] = []
        return self._conversations[session_id]

    def add_message(self, session_id: str, message: ChatMessage) -> None:
        """Add a message to the conversation."""
        conversation = self.get_or_create_conversation(session_id)
        conversation.append(message)

    def get_conversation(self, session_id: str) -> Optional[List[ChatMessage]]:
        """Get conversation by session ID."""
        return self._conversations.get(session_id)

    def delete_conversation(self, session_id: str) -> bool:
        """Delete conversation by session ID. Returns True if deleted, False if not found."""
        if session_id in self._conversations:
            del self._conversations[session_id]
            return True
        return False

    def session_exists(self, session_id: str) -> bool:
        """Check if session exists."""
        return session_id in self._conversations

    def get_message_count(self, session_id: str) -> int:
        """Get total message count for a session."""
        conversation = self._conversations.get(session_id, [])
        return len(conversation)
