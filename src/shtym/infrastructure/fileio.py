"""File I/O utilities for shtym infrastructure."""

from pathlib import Path


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

        Returns:
            The contents of the file as a string.
        """
        with self.file_path.open("r", encoding=encoding) as file:
            return file.read()
