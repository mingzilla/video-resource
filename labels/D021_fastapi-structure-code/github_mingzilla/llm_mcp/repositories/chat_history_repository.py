"""
Chat history repository for conversation storage and retrieval.

Provides singleton-based conversation management with repository pattern methods.
"""

from typing import Dict, List, Optional

from github_mingzilla.llm_mcp.models import ApiChatMessage
from github_mingzilla.llm_mcp.service_manager.singleton_manager import singleton_manager


class _ChatHistoryRepository:
    """
    Repository for chat conversation storage and retrieval.

    Provides conversation management using repository pattern.
    Current implementation uses in-memory storage.
    """

    def __init__(self):
        """Initialize chat history repository."""
        self._conversations: Dict[str, List[ApiChatMessage]] = {}

    def save_message_and_get_history(self, session_id: str, message: ApiChatMessage) -> List[ApiChatMessage]:
        """
        Save a message and return complete conversation history.

        Args:
            session_id: Unique session identifier
            message: Message to save

        Returns:
            Complete conversation history for the session
        """
        self.save_message(session_id, message)
        return self.get_conversation_history(session_id)

    def get_conversation_history(self, session_id: str) -> List[ApiChatMessage]:
        """
        Get conversation history, creating new conversation if needed.

        Args:
            session_id: Unique session identifier

        Returns:
            List of messages in chronological order
        """
        if session_id not in self._conversations:
            self._conversations[session_id] = []
        return self._conversations[session_id]

    def save_message(self, session_id: str, message: ApiChatMessage) -> None:
        """
        Save a message to the conversation history.

        Args:
            session_id: Unique session identifier
            message: Message to save
        """
        conversation = self.get_conversation_history(session_id)
        conversation.append(message)

    def find_conversation_by_id(self, session_id: str) -> Optional[List[ApiChatMessage]]:
        """
        Find conversation by session ID.

        Args:
            session_id: Unique session identifier

        Returns:
            Conversation messages if found, None otherwise
        """
        return self._conversations.get(session_id)

    def delete_conversation(self, session_id: str) -> bool:
        """
        Delete conversation by session ID.

        Args:
            session_id: Unique session identifier

        Returns:
            True if conversation was deleted, False if not found
        """
        if session_id in self._conversations:
            del self._conversations[session_id]
            return True
        return False

    def conversation_exists(self, session_id: str) -> bool:
        """
        Check if conversation exists.

        Args:
            session_id: Unique session identifier

        Returns:
            True if conversation exists, False otherwise
        """
        return session_id in self._conversations

    def get_message_count(self, session_id: str) -> int:
        """
        Get total message count for a conversation.

        Args:
            session_id: Unique session identifier

        Returns:
            Number of messages in the conversation
        """
        conversation = self._conversations.get(session_id, [])
        return len(conversation)

    def get_all_session_ids(self) -> List[str]:
        """
        Get all active session IDs.

        Returns:
            List of session identifiers
        """
        return list(self._conversations.keys())

    def clear_all_conversations(self) -> int:
        """
        Clear all conversations (useful for testing).

        Returns:
            Number of conversations that were cleared
        """
        count = len(self._conversations)
        self._conversations.clear()
        return count

    def get_conversation_summary(self) -> Dict[str, int]:
        """
        Get summary statistics for all conversations.

        Returns:
            Dictionary mapping session_id to message count
        """
        return {session_id: len(messages) for session_id, messages in self._conversations.items()}


# Module-level singleton instance
chat_history_repo = _ChatHistoryRepository()
singleton_manager.register(chat_history_repo)
