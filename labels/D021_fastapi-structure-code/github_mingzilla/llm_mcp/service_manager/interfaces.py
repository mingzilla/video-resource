"""
Interface definitions for service contracts.

Defines abstract base classes for common service patterns.
"""

from abc import ABC, abstractmethod


class ClosableService(ABC):
    """
    Interface for services that require cleanup on shutdown.

    Services that maintain connections, resources, or state that needs
    explicit cleanup should implement this interface.
    """

    @abstractmethod
    async def disconnect(self):
        """
        Disconnect and cleanup resources.

        This method should be implemented by services that need to:
        - Close network connections
        - Release file handles
        - Clean up background tasks
        - Flush pending operations
        """
        pass
