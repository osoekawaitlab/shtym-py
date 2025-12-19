"""Exceptions for shtym."""


class ShtymError(Exception):
    """Base exception for all shtym errors.

    All shtym exceptions should inherit from this base class
    to allow users to catch all shtym-related errors.
    """


class ShtymDomainError(ShtymError):
    """Base exception for domain layer errors.

    Domain errors represent business logic failures,
    such as invalid operations or unavailable resources.
    """


class ShtymInfrastructureError(ShtymError):
    """Base exception for infrastructure layer errors.

    Infrastructure errors relate to external systems,
    such as file I/O failures or network issues.
    """


class LLMModuleNotFoundError(ModuleNotFoundError, ShtymInfrastructureError):
    """Exception raised when LLM module is not found.

    This is an infrastructure-level error, not a domain error,
    as it relates to optional package installation.
    """

    def __init__(self, name_of_module: str) -> None:
        """Initialize the exception.

        Args:
            name_of_module: The name of the missing module.
        """
        super().__init__(f"{name_of_module} package is not installed")
        self.name_of_module = name_of_module
