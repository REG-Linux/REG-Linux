import json
from pathlib import Path
from typing import Any

from configgen.utils.logger import get_logger


class JSONSettings:
    """
    A class for managing JSON-based configuration settings with support for automatic file creation.

    This class provides methods to load, save, and manipulate configuration data stored in a JSON file.
    It includes error handling, logging, and support for nested key access.
    """

    __slots__ = ("filepath", "_data", "_logger")

    def __init__(self, filepath: str | Path, auto_load: bool = True) -> None:
        """
        Initialize the JSONSettings instance.

        Args:
            filepath (str | Path): The path to the JSON configuration file.
            auto_load (bool, optional): If True, automatically loads the JSON file on initialization.
                                       Defaults to True.
        """
        self.filepath = Path(
            filepath
        )  # Convert filepath to Path object for consistent handling
        self._data: dict[str, Any] = {}  # Internal dictionary to store JSON data
        self._logger = get_logger(f"{__name__}.JSONSettings")  # Logger for this class
        if auto_load:
            self.load()  # Load the JSON file if auto_load is True

    def _ensure_file_exists(self) -> None:
        """
        Ensure the JSON file exists, creating it with an empty dictionary if it doesn't.

        Creates parent directories if they don't exist and logs the creation or any errors.
        """
        if not self.filepath.exists():
            try:
                self.filepath.parent.mkdir(
                    parents=True, exist_ok=True
                )  # Create parent directories
                self.filepath.write_text(
                    "{}", encoding="utf-8"
                )  # Create empty JSON file
                self._logger.info(f"Created new JSON file: {self.filepath}")
            except Exception as e:
                self._logger.error(f"Failed to create JSON file {self.filepath}: {e}")

    def load(self, default: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        Load the JSON configuration file into memory.

        Args:
            default (dict[str, Any], optional): Default dictionary to use if loading fails.
                                               Defaults to None.

        Returns:
            dict[str, Any]: The loaded configuration data.
        """
        self._ensure_file_exists()  # Ensure the file exists before loading
        try:
            with self.filepath.open("r", encoding="utf-8") as f:
                self._data = json.load(f)  # Load JSON data into _data
        except Exception as e:
            self._logger.error(f"Failed to load JSON {self.filepath}: {e}")
            self._data = default or {}  # Use default or empty dict on failure
        return self._data

    def write(self, indent: int = 4) -> bool:
        """
        Write the current configuration data to the JSON file.

        Args:
            indent (int, optional): Number of spaces for JSON indentation. Defaults to 4.

        Returns:
            bool: True if writing was successful, False otherwise.
        """
        try:
            with self.filepath.open("w", encoding="utf-8") as f:
                json.dump(
                    self._data, f, indent=indent, ensure_ascii=False
                )  # Write data to file
            return True
        except Exception as e:
            self._logger.error(f"Failed to write JSON {self.filepath}: {e}")
            return False

    def save(self, name: str, value: Any) -> None:
        """
        Save a key-value pair to the configuration data.

        Args:
            name (str): The key to save.
            value (Any): The value to associate with the key.
        """
        self._data[name] = value  # Store the value in the internal dictionary

    def remove(self, name: str) -> bool:
        """
        Remove a key from the configuration data.

        Args:
            name (str): The key to remove.

        Returns:
            bool: True if the key was removed, False if it didn't exist.
        """
        return (
            self._data.pop(name, None) is not None
        )  # Remove and return True if key existed

    def exists(self, name: str) -> bool:
        """
        Check if a key exists in the configuration data.

        Args:
            name (str): The key to check.

        Returns:
            bool: True if the key exists, False otherwise.
        """
        return name in self._data

    def get(self, name: str, default: Any | None = None) -> Any | None:
        """
        Retrieve a value from the configuration data by key.

        Args:
            name (str): The key to retrieve.
            default (Any, optional): Default value to return if the key doesn't exist.
                                     Defaults to None.

        Returns:
            Optional[Any]: The value associated with the key, or the default value.
        """
        return self._data.get(name, default)

    def loadAll(self, name: str, includeName: bool = False) -> dict[str, str]:
        """
        Load all key-value pairs with keys starting with a given prefix.

        Args:
            name (str): The prefix to match keys against.
            includeName (bool, optional): If True, include the full key in the result.
                                        If False, strip the prefix. Defaults to False.

        Returns:
            Dict[str, str]: A dictionary containing the matching key-value pairs.
        """
        result = {}
        for key, value in self._data.items():
            if key.startswith(name + "."):
                suffix = (
                    key if includeName else key[len(name) + 1 :]
                )  # Strip prefix if needed
                result[suffix] = value
        return result

    def __getitem__(self, name: str) -> Any:
        """
        Allow dictionary-style access to configuration data (e.g., settings[key]).

        Args:
            name (str): The key to retrieve.

        Returns:
            Any: The value associated with the key.

        Raises:
            KeyError: If the key does not exist.
        """
        return self._data[name]

    def __setitem__(self, name: str, value: Any) -> None:
        """
        Allow dictionary-style assignment to configuration data (e.g., settings[key] = value).

        Args:
            name (str): The key to set.
            value (Any): The value to associate with the key.
        """
        self._data[name] = value

    def __contains__(self, name: str) -> bool:
        """
        Allow 'in' operator to check if a key exists in the configuration data.

        Args:
            name (str): The key to check.

        Returns:
            bool: True if the key exists, False otherwise.
        """
        return name in self._data
