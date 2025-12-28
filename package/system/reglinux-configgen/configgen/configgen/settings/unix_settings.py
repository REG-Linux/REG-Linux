from configparser import ConfigParser
from io import StringIO
from pathlib import Path
from typing import Any

from configgen.utils.logger import get_logger


class UnixSettings:
    """
    A class for managing INI/Unix-style configuration files with automatic file creation support.

    This class uses Python's `ConfigParser` to handle `.cfg` or `.ini`-style configuration files.
    It supports sections, preserves key case, and ensures compatibility with Unix-style key-value pairs.
    The class provides methods for loading, saving, and manipulating configuration data, with support
    for dictionary-like access and prefix-based key filtering.

    Example:
        settings = UnixSettings("config.cfg")
        settings.save("username", "admin")
        settings.write()
    """

    __slots__ = (
        "filepath",
        "separator",
        "comment",
        "config",
        "_logger",
        "_had_section",
    )

    def __init__(
        self, filepath: str | Path, separator: str = "", comment: str = "#"
    ) -> None:
        """
        Initialize the UnixSettings instance.

        Args:
            filepath (str | Path): Path to the INI/CFG configuration file.
            separator (str, optional): Separator used between key and value in the file. Defaults to "".
            comment (str, optional): Comment character used in the file. Defaults to "#".
        """
        self.filepath = Path(
            filepath
        )  # Convert filepath to Path object for consistent handling
        self.separator = separator  # Separator for key-value pairs in the file
        self.comment = comment  # Comment character for the configuration file
        self._logger = get_logger(f"{__name__}.UnixSettings")  # Logger for this class
        self._had_section = False  # Flag to track if the file contains section headers
        self._initialize_config()  # Initialize the ConfigParser

    def _ensure_file_exists(self) -> None:
        """
        Ensure the INI/CFG file exists, creating an empty one if it doesn't.

        Creates parent directories if necessary and logs the creation or any errors.
        """
        if not self.filepath.exists():
            try:
                self.filepath.parent.mkdir(
                    parents=True, exist_ok=True
                )  # Create parent directories
                self.filepath.write_text("", encoding="utf-8")  # Create empty file
                self._logger.info(f"Created new INI/CFG file: {self.filepath}")
            except Exception as e:
                self._logger.error(
                    f"Failed to create INI/CFG file {self.filepath}: {e}"
                )

    def _initialize_config(self) -> None:
        """
        Initialize the ConfigParser with Unix-friendly options.

        Configures the parser to disable interpolation, allow case-sensitive keys,
        and permit keys without values.
        """
        self.config = ConfigParser(
            interpolation=None, strict=False, allow_no_value=True
        )
        self.config.optionxform = lambda optionstr: str(optionstr)  # Preserve key case
        self._load_file()  # Load the configuration file

    def _load_file(self) -> None:
        """
        Load the INI/CFG file into memory.

        If the file lacks section headers, it wraps the content in a `[DEFAULT]` section
        for compatibility with ConfigParser. Logs any errors during loading.
        """
        self._ensure_file_exists()  # Ensure the file exists before loading
        try:
            content = self.filepath.read_text(encoding="utf-8")  # Read file content
            # Check if the file contains any section headers
            self._had_section = any(
                line.strip().startswith("[") and line.strip().endswith("]")
                for line in content.splitlines()
                if line.strip()
            )
            # If no section headers, prepend `[DEFAULT]` to the content
            if not self._had_section and content.strip():
                content = "[DEFAULT]\n" + content
            with StringIO(content) as buffer:
                self.config.read_file(buffer)  # Load content into ConfigParser
        except Exception as e:
            self._logger.error(f"Failed to load INI/CFG {self.filepath}: {e}")

    def ensure_section(self, section: str) -> None:
        """
        Ensure a section exists in the configuration.

        Args:
            section (str): The section name to ensure exists.
        """
        if not self.config.has_section(section) and section != "DEFAULT":
            self.config.add_section(section)  # Add section if it doesn't exist

    def set(self, section: str, name: str, value: str | int | float | bool) -> None:
        """
        Set a key-value pair in a specific section.

        Args:
            section (str): The section to store the key-value pair in.
            name (str): The key name.
            value (Union[str, int, float, bool]): The value to store (converted to string).
        """
        self.ensure_section(section)  # Ensure the section exists
        self.config.set(section, name, str(value))  # Set the value

    def has_section(self, section: str) -> bool:
        """
        Check if a section exists in the configuration.

        Args:
            section (str): The section name to check.

        Returns:
            bool: True if the section exists, False otherwise.
        """
        return self.config.has_section(section)

    def has_option(self, section: str, option: str) -> bool:
        """
        Check if a specific option exists in a section.

        Args:
            section (str): The section to check.
            option (str): The option (key) to check.

        Returns:
            bool: True if the option exists, False otherwise.
        """
        return self.config.has_option(section, option)

    def load(self, default: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        Load the `[DEFAULT]` section into a dictionary.

        Args:
            default (dict[str, Any], optional): Fallback dictionary if loading fails. Defaults to None.

        Returns:
            dict[str, Any]: Dictionary of key-value pairs from the `[DEFAULT]` section.
        """
        if self.config.has_section("DEFAULT"):
            return dict(
                self.config.items("DEFAULT")
            )  # Return items from DEFAULT section
        return default or {}  # Return default or empty dict if section is missing

    def write(self) -> bool:
        """
        Write the in-memory configuration to the file.

        Returns:
            bool: True if writing was successful, False otherwise.
        """
        try:
            with self.filepath.open("w", encoding="utf-8") as f:
                self.config.write(
                    f, space_around_delimiters=bool(self.separator)
                )  # Write to file
            return True
        except Exception as e:
            self._logger.error(f"Failed to write INI/CFG {self.filepath}: {e}")
            return False

    def save_file(self) -> bool:
        """
        Alias for `write()` to maintain compatibility with other code.

        Returns:
            bool: True if writing was successful, False otherwise.
        """
        return self.write()

    def save(self, name: str, value: str | int | float | bool) -> None:
        """
        Save a key-value pair in the `[DEFAULT]` section.

        Args:
            name (str): The key name.
            value (Union[str, int, float, bool]): The value to store (converted to string).
        """
        self.config.set("DEFAULT", name, str(value))  # Set value in DEFAULT section

    def remove(self, name: str) -> bool:
        """
        Remove a key from the `[DEFAULT]` section.

        Args:
            name (str): The key to remove.

        Returns:
            bool: True if the key was removed, False if it didn't exist.
        """
        return self.config.remove_option("DEFAULT", name)

    def exists(self, name: str) -> bool:
        """
        Check if a key exists in the `[DEFAULT]` section.

        Args:
            name (str): The key to check.

        Returns:
            bool: True if the key exists, False otherwise.
        """
        return self.config.has_option("DEFAULT", name)

    def get(self, name: str, default: Any | None = None) -> Any | None:
        """
        Retrieve a value from the `[DEFAULT]` section.

        Args:
            name (str): The key name.
            default (Any, optional): Value to return if the key is missing. Defaults to None.

        Returns:
            Optional[Any]: The stored value or the default value if the key is missing.
        """
        return self.config.get("DEFAULT", name, fallback=default)

    def loadAll(self, name: str, includeName: bool = False) -> dict[str, str]:
        """
        Load all keys in the `[DEFAULT]` section that start with a given prefix.

        Args:
            name (str): Prefix to filter keys.
            includeName (bool, optional): If True, include the full key name in the result.
                                        If False, strip the prefix. Defaults to False.

        Returns:
            Dict[str, str]: Dictionary of matching key-value pairs.
        """
        result = {}
        for key, value in self.config.items("DEFAULT"):
            if key.startswith(name + "."):
                suffix = (
                    key if includeName else key[len(name) + 1 :]
                )  # Strip prefix if needed
                result[suffix] = value
        return result

    def __getitem__(self, name: str) -> str:
        """
        Allow dictionary-style access to the `[DEFAULT]` section (e.g., settings[key]).

        Args:
            name (str): The key to retrieve.

        Returns:
            str: The value associated with the key.

        Raises:
            KeyError: If the key does not exist.
        """
        val = self.get(name)
        if val is None:
            raise KeyError(name)
        return val

    def __setitem__(self, name: str, value: Any) -> None:
        """
        Allow dictionary-style assignment to the `[DEFAULT]` section (e.g., settings[key] = value).

        Args:
            name (str): The key to set.
            value (Any): The value to store.
        """
        self.save(name, value)

    def __contains__(self, name: str) -> bool:
        """
        Allow 'in' operator to check if a key exists in the `[DEFAULT]` section.

        Args:
            name (str): The key to check.

        Returns:
            bool: True if the key exists, False otherwise.
        """
        return self.exists(name)
