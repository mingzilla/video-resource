"""
Singleton management system for centralized resource lifecycle.

Provides registration and cleanup for all singleton instances in the application.
"""

from typing import Any, List

from github_mingzilla.llm_mcp.service_manager.interfaces import ClosableService


class _SingletonManager:
    """
    Manages all singleton instances in the application.

    Provides centralized registration and cleanup for singleton services.
    All singletons can be registered, but only ClosableService instances
    will have their disconnect() method called during shutdown.
    """

    def __init__(self):
        self._singletons: List[Any] = []

    def register(self, instance: Any):
        """
        Register a singleton instance.

        Args:
            instance: Any singleton instance to register
        """
        self._singletons.append(instance)
        print(f"Registered singleton: {instance.__class__.__name__}")

    async def shutdown_all(self):
        """
        Shutdown all registered closable services.

        Iterates through all registered singletons and calls disconnect()
        only on instances that implement ClosableService interface.
        """
        try:
            for instance in self._singletons:
                if isinstance(instance, ClosableService):
                    try:
                        await instance.disconnect()
                        print(f"Disconnected {instance.__class__.__name__} successfully")
                    except Exception as e:
                        print(f"Error disconnecting {instance.__class__.__name__}: {e}")
            print("All closable singleton services cleaned up successfully")
        except Exception as e:
            print(f"Error during singleton cleanup: {e}")
            raise

    def get_registered_count(self) -> int:
        """
        Get the number of registered singletons.

        Returns:
            Number of registered singleton instances
        """
        return len(self._singletons)

    def get_closable_count(self) -> int:
        """
        Get the number of closable services registered.

        Returns:
            Number of singletons that implement ClosableService
        """
        return sum(1 for instance in self._singletons if isinstance(instance, ClosableService))

    def reset_all(self):
        """
        Reset all registered singletons.

        Useful for testing scenarios where you need to clear the registry.
        """
        self._singletons.clear()
        print("All singleton registrations cleared")


# Module-level singleton manager instance
singleton_manager = _SingletonManager()
