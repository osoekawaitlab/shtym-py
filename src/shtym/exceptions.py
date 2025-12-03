"""Exceptions for shtym domain layer."""


class BaseShtymError(Exception):
    """Base exception for shtym domain layer."""


class LLMModuleNotFoundError(ModuleNotFoundError, BaseShtymError):
    """Exception raised when LLM module is not found."""

    def __init__(self, name_of_module: str) -> None:
        """Initialize the exception.

        Args:
            name_of_module: The name of the missing module.
        """
        super().__init__(f"{name_of_module} package is not installed")
        self.name_of_module = name_of_module
