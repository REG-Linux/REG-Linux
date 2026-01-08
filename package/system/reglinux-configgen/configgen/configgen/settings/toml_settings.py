from pathlib import Path
from typing import Any

from configgen.utils.logger import get_logger

# Import TOML libraries with type annotations
try:
    import toml
    import tomli_w
except ImportError:
    import sys

    print(
        "Error: toml and tomli_w modules are required for TOMLSettings",
        file=sys.stderr,
    )
    raise


class TOMLSettings:
    """A class for managing TOML-based configuration settings with support for automatic file creation.

    This class provides methods to load, save, and manipulate configuration data stored in a TOML file.
    It includes error handling, logging, and support for nested key access.
    """

    __slots__ = ("_data", "_logger", "filepath")

    def __init__(self, filepath: str | Path, auto_load: bool = True) -> None:
        """Initialize the TOMLSettings instance.

        Args:
            filepath (str | Path): The path to the TOML configuration file.
            auto_load (bool, optional): If True, automatically loads the TOML file on initialization.
                                       Defaults to True.

        """
        self.filepath = Path(
            filepath,
        )  # Convert filepath to Path object for consistent handling
        self._data: dict[str, Any] = {}  # Internal dictionary to store TOML data
        self._logger = get_logger(f"{__name__}.TOMLSettings")  # Logger for this class
        if auto_load:
            self.load()  # Load the TOML file if auto_load is True

    def _ensure_file_exists(self) -> None:
        """Ensure the TOML file exists, creating it with an empty dictionary if it doesn't.

        Creates parent directories if they don't exist and logs the creation or any errors.
        """
        if not self.filepath.exists():
            try:
                self.filepath.parent.mkdir(
                    parents=True,
                    exist_ok=True,
                )  # Create parent directories
                self.filepath.write_text(
                    "# Configuration file\n",
                    encoding="utf-8",
                )  # Create empty TOML file
                self._logger.info(f"Created new TOML file: {self.filepath}")
            except Exception as e:
                self._logger.error(f"Failed to create TOML file {self.filepath}: {e}")

    def load(self, default: dict[str, Any] | None = None) -> dict[str, Any]:
        """Load the TOML configuration file into memory.

        Args:
            default (Optional[Dict[str, Any]], optional): Default dictionary to use if loading fails.
                                               Defaults to None.

        Returns:
            Dict[str, Any]: The loaded configuration data.

        """
        self._ensure_file_exists()  # Ensure the file exists before loading
        try:
            with self.filepath.open("r", encoding="utf-8") as f:
                self._data = toml.load(f)  # Load TOML data into _data
        except Exception as e:
            self._logger.error(f"Failed to load TOML {self.filepath}: {e}")
            self._data = default or {}  # Use default or empty dict on failure
        return self._data

    def write(self) -> bool:
        """Write the current configuration data to the TOML file.

        Args:
            indent (int, optional): Number of spaces for JSON indentation. Defaults to 4.

        Returns:
            bool: True if writing was successful, False otherwise.

        """
        try:
            with self.filepath.open("wb") as f:
                tomli_w.dump(self._data, f)  # Write data to file
            return True
        except Exception as e:
            self._logger.error(f"Failed to write TOML {self.filepath}: {e}")
            return False

    def save(self, name: str, value: Any) -> None:
        """Save a key-value pair to the configuration data.

        Args:
            name (str): The key to save.
            value (Any): The value to associate with the key.

        """
        self._data[name] = value  # Store the value in the internal dictionary

    def remove(self, name: str) -> bool:
        """Remove a key from the configuration data.

        Args:
            name (str): The key to remove.

        Returns:
            bool: True if the key was removed, False if it didn't exist.

        """
        return (
            self._data.pop(name, None) is not None
        )  # Remove and return True if key existed

    def exists(self, name: str) -> bool:
        """Check if a key exists in the configuration data.

        Args:
            name (str): The key to check.

        Returns:
            bool: True if the key exists, False otherwise.

        """
        return name in self._data

    def get(self, name: str, default: Any | None = None) -> Any | None:
        """Retrieve a value from the configuration data by key.

        Args:
            name (str): The key to retrieve.
            default (Any, optional): Default value to return if the key doesn't exist.
                                     Defaults to None.

        Returns:
            Optional[Any]: The value associated with the key, or the default value.

        """
        return self._data.get(name, default)

    def loadAll(self, name: str, includeName: bool = False) -> dict[str, Any]:
        """Load all key-value pairs with keys starting with a given prefix.

        Args:
            name (str): The prefix to match keys against.
            includeName (bool, optional): If True, include the full key in the result.
                                        If False, strip the prefix. Defaults to False.

        Returns:
            Dict[str, Any]: A dictionary containing the matching key-value pairs.

        """
        result: dict[str, Any] = {}
        for key, value in self._data.items():
            if key.startswith(name + "."):
                suffix = (
                    key if includeName else key[len(name) + 1 :]
                )  # Strip prefix if needed
                result[suffix] = value
        return result

    def __getitem__(self, name: str) -> Any:
        """Allow dictionary-style access to configuration data (e.g., settings[key]).

        Args:
            name (str): The key to retrieve.

        Returns:
            Any: The value associated with the key.

        Raises:
            KeyError: If the key does not exist.

        """
        return self._data[name]

    def __setitem__(self, name: str, value: Any) -> None:
        """Allow dictionary-style assignment to configuration data (e.g., settings[key] = value).

        Args:
            name (str): The key to set.
            value (Any): The value to associate with the key.

        """
        self._data[name] = value

    def __contains__(self, name: str) -> bool:
        """Allow 'in' operator to check if a key exists in the configuration data.

        Args:
            name (str): The key to check.

        Returns:
            bool: True if the key exists, False otherwise.

        """
        return name in self._data
