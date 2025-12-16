"""File I/O utilities for shtym infrastructure."""

from pathlib import Path

from shtym.exceptions import ShtymInfrastructureError


class FileReadError(ShtymInfrastructureError):
    """Exception raised when file reading fails."""

    def __init__(self, message: str) -> None:
        """Initialize the exception.

        Args:
            message: The error message.
        """
        super().__init__(f"File read error: {message}")


class FileReader:
    """Utility class for reading files.

    Supposed to be used in reading not-so large files like configuration files.
    """

    def __init__(self, file_path: Path) -> None:
        """Initialize the FileReader with a file path.

        Args:
            file_path: The path to the file to read.
        """
        self.file_path = file_path

    def read_str(self, encoding: str) -> str:
        """Read the contents of the file.

        Args:
            encoding: The encoding to use when reading the file.

        Returns:
            The contents of the file as a string.

        Raises:
            FileReadError: If the file cannot be read.
        """
        try:
            with self.file_path.open("r", encoding=encoding) as file:
                return file.read()
        except FileNotFoundError as e:
            msg = f"File not found: {self.file_path}"
            raise FileReadError(msg) from e
        except OSError as e:
            msg = f"Cannot read file {self.file_path}: {e}"
            raise FileReadError(msg) from e
