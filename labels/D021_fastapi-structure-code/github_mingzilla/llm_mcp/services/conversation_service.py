"""
Conversation service for managing conversation state and operations.

Handles conversation CRUD operations and message management.
"""

from typing import Dict, List, Optional

from github_mingzilla.llm_mcp.boundary_models import ApiChatMessage
from github_mingzilla.llm_mcp.repositories.chat_history_repository import chat_history_repo
from github_mingzilla.llm_mcp.service_manager.singleton_manager import singleton_manager


class _ConversationService:
    """
    Service for conversation management.
    """

    def __init__(self):
        """Initialize conversation service with singleton repository."""
        self.chat_history_repo = chat_history_repo

    def get_conversation_details(self, session_id: str) -> Dict:
        """
        Get complete conversation details for a session.

        Args:
            session_id: Session identifier

        Returns:
            Dictionary with conversation details

        Raises:
            ValueError: If session not found
        """
        conversation = self.chat_history_repo.find_conversation_by_id(session_id)
        if conversation is None:
            raise ValueError(f"Session {session_id} not found")

        return {
            "session_id": session_id,
            "messages": [msg.dict() for msg in conversation],
            "message_count": self.chat_history_repo.get_message_count(session_id),
        }

    def delete_conversation(self, session_id: str) -> bool:
        """
        Delete a conversation by session ID.

        Args:
            session_id: Session identifier

        Returns:
            True if conversation was deleted, False if not found
        """
        return self.chat_history_repo.delete_conversation(session_id)

    def add_message_to_conversation(self, session_id: str, message_data: Dict) -> Dict:
        """
        Add a message to an existing conversation.

        Args:
            session_id: Session identifier
            message_data: Message data dictionary

        Returns:
            Updated conversation summary

        Raises:
            ValueError: If message data is invalid
        """
        # Validate message data
        if not message_data.get("role") or not message_data.get("content"):
            raise ValueError("Message must have 'role' and 'content' fields")

        # Create message object
        message = ApiChatMessage(role=message_data["role"], content=message_data["content"], tool_calls=message_data.get("tool_calls"))

        # Save message
        self.chat_history_repo.save_message(session_id, message)

        return {
            "session_id": session_id,
            "message": "Message added successfully",
            "message_count": self.chat_history_repo.get_message_count(session_id),
        }

    def get_conversation_summary(self, session_id: str) -> Dict:
        """
        Get a summary of conversation metadata.

        Args:
            session_id: Session identifier

        Returns:
            Dictionary with conversation metadata
        """
        if not self.chat_history_repo.conversation_exists(session_id):
            return {"session_id": session_id, "exists": False, "message_count": 0}

        conversation = self.chat_history_repo.find_conversation_by_id(session_id)

        # Calculate conversation statistics
        user_messages = sum(1 for msg in conversation if msg.role == "user")
        assistant_messages = sum(1 for msg in conversation if msg.role == "assistant")
        tool_messages = sum(1 for msg in conversation if msg.role == "tool")

        last_message = conversation[-1] if conversation else None

        return {"session_id": session_id, "exists": True, "message_count": len(conversation), "user_messages": user_messages, "assistant_messages": assistant_messages, "tool_messages": tool_messages, "last_message_role": last_message.role if last_message else None, "last_message_timestamp": getattr(last_message, "timestamp", None) if last_message else None}

    def get_conversation_messages(self, session_id: str, limit: Optional[int] = None) -> List[ApiChatMessage]:
        """
        Get conversation messages with optional limit.

        Args:
            session_id: Session identifier
            limit: Optional limit on number of messages to return

        Returns:
            List of conversation messages
        """
        conversation = self.chat_history_repo.find_conversation_by_id(session_id)
        if conversation is None:
            return []

        if limit is not None and limit > 0:
            return conversation[-limit:]  # Return last N messages

        return conversation

    def clear_conversation(self, session_id: str) -> bool:
        """
        Clear all messages from a conversation (but keep the session).

        Args:
            session_id: Session identifier

        Returns:
            True if conversation was cleared, False if session didn't exist
        """
        if not self.chat_history_repo.conversation_exists(session_id):
            return False

        # Delete and recreate empty conversation
        self.chat_history_repo.delete_conversation(session_id)
        self.chat_history_repo.get_conversation_history(session_id)  # Creates empty conversation

        return True

    def get_all_sessions(self) -> List[Dict]:
        """
        Get summary information for all active sessions.

        Returns:
            List of session summaries
        """
        all_sessions = self.chat_history_repo.get_all_session_ids()
        summary_data = self.chat_history_repo.get_conversation_summary()

        return [{"session_id": session_id, "message_count": summary_data.get(session_id, 0)} for session_id in all_sessions]

    def validate_session_id(self, session_id: str) -> None:
        """
        Validate session ID format and existence requirements.

        Args:
            session_id: Session identifier to validate

        Raises:
            ValueError: If session ID is invalid
        """
        if not session_id or not session_id.strip():
            raise ValueError("Session ID cannot be empty")

        if len(session_id) > 100:  # Reasonable limit
            raise ValueError("Session ID too long")

    def validate_message_data(self, message_data: Dict) -> None:
        """
        Validate message data structure.

        Args:
            message_data: Message data to validate

        Raises:
            ValueError: If message data is invalid
        """
        required_fields = ["role", "content"]
        for field in required_fields:
            if field not in message_data:
                raise ValueError(f"Missing required field: {field}")

        valid_roles = ["user", "assistant", "tool", "system"]
        if message_data["role"] not in valid_roles:
            raise ValueError(f"Invalid role. Must be one of: {valid_roles}")

        if not message_data["content"] or not str(message_data["content"]).strip():
            raise ValueError("Message content cannot be empty")


# Module-level singleton instance
conversation_service = _ConversationService()
singleton_manager.register(conversation_service)
