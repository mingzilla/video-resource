"""
Tool orchestration service for managing complex tool workflows.

Handles progressive tool orchestration with streaming responses.
"""

from collections.abc import AsyncIterator
from typing import List

from github_mingzilla.llm_mcp.boundary_models import ApiChatMessage, DomainMcpTool, LlmResponse
from github_mingzilla.llm_mcp.clients.llm_client import llm_client
from github_mingzilla.llm_mcp.clients.mcp_client import mcp_client
from github_mingzilla.llm_mcp.repositories.chat_history_repository import chat_history_repo
from github_mingzilla.llm_mcp.service_manager.singleton_manager import singleton_manager


class _ToolOrchestrationService:
    """
    Service for tool orchestration.
    """

    def __init__(self):
        """Initialize tool orchestration service with singleton dependencies."""
        self.llm_client = llm_client
        self.mcp_client = mcp_client
        self.chat_history_repo = chat_history_repo

    async def orchestrate_tools_streaming(self, session_id: str, model: str, mcp_tools: List[DomainMcpTool], iteration: int = 0) -> AsyncIterator[LlmResponse]:
        """
        Progressive tool orchestration with streaming responses.

        Yields each LLM response immediately while continuing tool processing.
        Follows recursive pattern for multi-step tool workflows.

        Args:
            session_id: The session ID for the conversation
            model: The model to use for completion
            mcp_tools: Pre-filtered list of DomainMcpTool objects
            iteration: Current recursion depth (for protection)

        Yields:
            Each LLM response as it becomes available

        Raises:
            Exception: If tool orchestration fails
        """
        # Prevent infinite recursion
        if iteration >= 5:
            error_response = self._create_error_response("Maximum tool call iterations reached.")
            yield error_response
            return

        try:
            # Get conversation history
            conversation = self.chat_history_repo.get_conversation_history(session_id)

            # Send conversation + tools to LLM
            llm_response = await self.llm_client.invoke(messages=conversation, model=model, mcp_tools=mcp_tools)

            # Convert generic tool calls to ChatMessage dict format
            tool_calls_dict = llm_response.to_chat_message_dict()

            # Add assistant message to history
            assistant_message = ApiChatMessage(
                role="assistant",
                content=llm_response.content,
                tool_calls=tool_calls_dict,
            )
            self.chat_history_repo.save_message(session_id, assistant_message)

            # Yield current LLM response
            yield llm_response

            # Check if tools were called
            if not llm_response.has_tool_calls():
                # No tools called - orchestration complete
                return

            # Execute all tool calls in parallel using MCPClient
            tool_messages = await self.mcp_client.execute_tools_parallel(llm_response.get_tool_execution_data(mcp_tools))

            # Add all tool results to conversation
            for tool_message in tool_messages:
                self.chat_history_repo.save_message(session_id, tool_message)

            # Recursive case: tools were called, continue for next LLM round
            async for next_response in self.orchestrate_tools_streaming(session_id, model, mcp_tools, iteration + 1):
                yield next_response

        except Exception as e:
            error_response = self._create_error_response(f"Error during tool orchestration: {str(e)}")
            yield error_response

    async def discover_available_tools(self) -> dict:
        """
        Discover all available MCP tools from all servers.

        Returns:
            Dictionary with tools, count, and server information
        """
        try:
            tools = await self.mcp_client.discover_tools()

            # Convert DomainMcpTool objects to dict for JSON response
            tools_dict = [tool.model_dump() for tool in tools]

            # Get server configuration information
            return {
                "tools": tools_dict,
                "count": len(tools),
                "mcp_servers": self.mcp_client.server_mapping,
            }
        except Exception as e:
            raise Exception(f"Failed to discover tools: {str(e)}")

    async def get_filtered_tools(self, selected_tools: List) -> List[DomainMcpTool]:
        """
        Get filtered tools based on selection criteria.

        Args:
            selected_tools: List of tool selection criteria

        Returns:
            Filtered list of available tools
        """
        return await self.mcp_client.get_filtered_tools(selected_tools)

    async def execute_single_tool_workflow(self, session_id: str, model: str, tool_selection: List, max_iterations: int = 3) -> List[LlmResponse]:
        """
        Execute a simple tool workflow with limited iterations.

        Args:
            session_id: Session identifier
            model: LLM model to use
            tool_selection: Selected tools for workflow
            max_iterations: Maximum orchestration iterations

        Returns:
            List of all LLM responses from the workflow
        """
        filtered_tools = await self.get_filtered_tools(tool_selection)
        responses = []

        async for response in self.orchestrate_tools_streaming(session_id, model, filtered_tools, 0):
            responses.append(response)
            # Limit iterations for single workflow
            if len(responses) >= max_iterations:
                break

        return responses

    def validate_tool_request(self, selected_tools: List) -> None:
        """
        Validate tool selection request.

        Args:
            selected_tools: Tools selected for orchestration

        Raises:
            ValueError: If validation fails
        """
        if not selected_tools:
            raise ValueError("At least one tool must be selected for orchestration")

        # Additional validation could be added here
        # e.g., check tool compatibility, permissions, etc.

    def get_orchestration_status(self, session_id: str) -> dict:
        """
        Get current orchestration status for a session.

        Args:
            session_id: Session identifier

        Returns:
            Dictionary with orchestration statistics
        """
        conversation = self.chat_history_repo.find_conversation_by_id(session_id)
        if not conversation:
            return {"status": "no_conversation", "message_count": 0}

        tool_message_count = sum(1 for msg in conversation if hasattr(msg, "tool_calls") and msg.tool_calls)

        return {"status": "active" if conversation else "no_conversation", "total_messages": len(conversation), "tool_messages": tool_message_count, "last_message_role": conversation[-1].role if conversation else None}

    def _create_error_response(self, error_message: str) -> LlmResponse:
        """
        Create an error response in LlmResponse format.

        Args:
            error_message: Error message to include

        Returns:
            LlmResponse with error content
        """

        # This is a simplified error response
        # In a real implementation, this would use the actual LlmResponse constructor
        class ErrorResponse:
            def __init__(self, message: str):
                self.content = message
                self.model = "error"
                self.usage = None

            def get_status_text(self) -> str:
                return self.content

            def has_tool_calls(self) -> bool:
                return False

        return ErrorResponse(error_message)


# Module-level singleton instance
tool_orchestration_service = _ToolOrchestrationService()
singleton_manager.register(tool_orchestration_service)
