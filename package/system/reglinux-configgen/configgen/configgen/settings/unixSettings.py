"""
UnixSettings - Optimized Configuration File Manager

This module provides an optimized implementation for managing Unix-style configuration files.
It uses ConfigParser as backend with significant performance improvements and modern Python features.

Key Features:
- Handles both sectioned and non-sectioned configuration files transparently
- Provides caching for improved performance with repeated reads
- Supports various data types (string, int, float, bool)
- Includes safe string handling for configuration keys
- Implements dictionary-like interface for easy access
- Optimized file I/O with buffering
"""

from configparser import ConfigParser
from os import path
from re import compile as re_compile, Pattern
from io import StringIO
from typing import Dict, Optional, Union
import logging

# Cache for compiled regular expressions to improve performance
_REGEX_CACHE: Dict[str, Pattern[str]] = {}

# Regular expression for sanitizing configuration keys
_PROTECT_STRING_REGEX = re_compile(r'[^A-Za-z0-9-\.]+')

class UnixSettings:
    """
    A high-performance configuration file manager for Unix-style settings files.

    This class provides methods to read, write, and manage configuration files
    with support for both traditional key=value formats and sectioned INI formats.

    Attributes:
        settingsFile (str): Path to the configuration file
        separator (str): Optional separator used around equals sign when writing
        comment (str): Character used for comments in the file
        config (ConfigParser): The underlying configuration parser instance
    """

    __slots__ = ('settingsFile', 'separator', 'comment', 'config', '_logger', '_data_cache', '_had_section')

    def __init__(self, settingsFile: str, separator: str = '', defaultComment: str = '#'):
        """
        Initialize the UnixSettings instance.

        Args:
            settingsFile: Path to the configuration file
            separator: Optional separator to use around equals sign (e.g., ' ' for 'key = value')
            defaultComment: Comment character to use (defaults to '#')

        Raises:
            ValueError: If settingsFile is empty
        """
        if not settingsFile:
            raise ValueError("Settings file path cannot be empty")

        self.settingsFile = settingsFile
        self.separator = separator
        self.comment = defaultComment
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._data_cache = None  # Cache for loaded data to improve performance
        self._had_section = False  # Tracks if the original file had sections
        self._initialize_config()

    def _initialize_config(self) -> None:
        """Initialize the ConfigParser instance with optimized settings."""
        self._logger.debug(f"Initializing optimized parser for {self.settingsFile}")
        self.config = ConfigParser(
            interpolation=None,  # Disable interpolation for better performance
            strict=False,       # Allow duplicate options
            allow_no_value=True,  # Support keys without values
            delimiters=('=',),    # Only allow '=' as delimiter
            comment_prefixes=('#', ';')  # Standard comment characters
        )
        # Preserve case sensitivity for option names
        self.config.optionxform = lambda optionstr: str(optionstr)
        self._load_file()

    def _load_file(self) -> None:
        """
        Load the configuration file from disk.

        Handles both sectioned and non-sectioned files transparently by
        automatically adding a [DEFAULT] section if no sections are present.
        """
        if not path.exists(self.settingsFile):
            return

        try:
            with open(self.settingsFile, 'r', encoding='utf-8-sig', buffering=8192) as file:
                content = file.read()

            # Detect if file had sections originally
            self._had_section = any(
                line.strip().startswith('[') and line.strip().endswith(']')
                for line in content.splitlines() if line.strip()
            )

            # If no sections found, add [DEFAULT] section in memory
            if not self._had_section:
                self._logger.debug(f"No section headers found in {self.settingsFile}, adding [DEFAULT] in memory")
                content = "[DEFAULT]\n" + content

            with StringIO(content) as config_file:
                self.config.read_file(config_file)

        except (IOError, OSError) as e:
            self._logger.error(f"IO error loading configuration file {self.settingsFile}: {e}")
        except Exception as e:
            self._logger.error(f"Unexpected error loading configuration file {self.settingsFile}: {e}")

    def write(self) -> bool:
        """
        Write the current configuration to disk.

        Returns:
            bool: True if write was successful, False otherwise

        Note:
            Maintains the original file format (sectioned or non-sectioned)
            and preserves the separator style if specified.
        """
        try:
            config_lines = []
            # Handle non-sectioned files (original format)
            if not self._had_section:
                for key, value in self.config.items('DEFAULT'):
                    if self.separator:
                        line = f"{key}{self.separator}={self.separator}{value}\n"
                    else:
                        line = f"{key}={value}\n"
                    config_lines.append(line)
            else:
                # Maintain sectioned format
                with StringIO() as output:
                    self.config.write(output, space_around_delimiters=bool(self.separator))
                    return self._write_to_disk(output.getvalue())

            return self._write_to_disk("".join(config_lines))

        except (IOError, OSError) as e:
            self._logger.error(f"IO error writing configuration file {self.settingsFile}: {e}")
            return False
        except Exception as e:
            self._logger.error(f"Unexpected error writing configuration file: {e}")
            return False

    def _write_to_disk(self, content: str) -> bool:
        """
        Internal method to write content to disk.

        Args:
            content: The string content to write

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(self.settingsFile, 'w', encoding='utf-8', buffering=8192) as fp:
                fp.write(content)
            self._data_cache = None  # Clear cache after write
            return True
        except Exception as e:
            self._logger.error(f"Error writing to disk: {e}")
            return False

    def save(self, name: str, value: Union[str, int, float, bool]) -> None:
        """
        Save a configuration value.

        Args:
            name: The configuration key
            value: The value to store (will be converted to string)

        Raises:
            ValueError: If name is empty
        """
        if not name:
            raise ValueError("Configuration name cannot be empty")
        str_value = str(value)
        if "password" in name.lower():
            self._logger.debug(f"Writing {name} = ******** to {self.settingsFile}")
        else:
            self._logger.debug(f"Writing {name} = {str_value} to {self.settingsFile}")
        self.config.set('DEFAULT', name, str_value)
        self._data_cache = None  # Invalidate cache after modification

    def disableAll(self, name: str) -> int:
        """
        Remove all settings with a given prefix.

        Args:
            name: The prefix to match against configuration keys

        Returns:
            int: Number of settings removed
        """
        if not name:
            return 0
        self._logger.debug(f"Removing all settings with prefix '{name}' from {self.settingsFile}")
        keys_to_remove = [key for key in self.config.options('DEFAULT') if key.startswith(name)]
        for key in keys_to_remove:
            self.config.remove_option('DEFAULT', key)
        if keys_to_remove:
            self._data_cache = None  # Invalidate cache if changes were made
        return len(keys_to_remove)

    def remove(self, name: str) -> bool:
        """
        Remove a specific configuration setting.

        Args:
            name: The key to remove

        Returns:
            bool: True if the key was found and removed, False otherwise
        """
        try:
            result = self.config.remove_option('DEFAULT', name)
            if result:
                self._data_cache = None  # Invalidate cache if change was made
            return result
        except Exception:
            return False

    def get(self, name: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get a configuration value.

        Args:
            name: The key to look up
            default: Default value to return if key not found

        Returns:
            The configuration value as string, or default if not found
        """
        try:
            return self.config.get('DEFAULT', name)
        except:
            return default

    def exists(self, name: str) -> bool:
        """
        Check if a configuration key exists.

        Args:
            name: The key to check

        Returns:
            bool: True if key exists, False otherwise
        """
        return self.config.has_option('DEFAULT', name)

    @staticmethod
    def protectString(input_str: str) -> str:
        """
        Sanitize a string to be safe for use as configuration key.

        Args:
            input_str: The string to sanitize

        Returns:
            str: Sanitized string with only alphanumeric, dash and dot characters
        """
        if not input_str:
            return ''
        return _PROTECT_STRING_REGEX.sub('_', input_str)

    def loadAll(self, name: str, includeName: bool = False) -> Dict[str, str]:
        """
        Load all settings with a given prefix.

        Args:
            name: The prefix to match
            includeName: If True, includes the prefix in returned keys

        Returns:
            Dict[str, str]: Dictionary of matching key-value pairs
        """
        if not name:
            return {}
        self._logger.debug(f"Looking for {name}.* in {self.settingsFile}")
        cache_key = f"{name}_{includeName}"
        # Return cached result if available
        if not includeName and self._data_cache and cache_key in self._data_cache:
            return self._data_cache[cache_key].copy()

        # Compile regex if not cached
        if name not in _REGEX_CACHE:
            pattern = f"^{self.protectString(name)}\\.(.+)"
            _REGEX_CACHE[name] = re_compile(pattern)

        regex = _REGEX_CACHE[name]
        result = {}
        for key, value in self.config.items('DEFAULT'):
            protected_key = self.protectString(key)
            match = regex.match(protected_key)
            if match:
                suffix = match.group(1)
                result_key = f"{name}.{suffix}" if includeName else suffix
                result[result_key] = value

        # Update cache
        if not self._data_cache:
            self._data_cache = {}
        self._data_cache[cache_key] = result.copy()
        return result

    def getAllKeys(self) -> list:
        """
        Get all configuration keys.

        Returns:
            list: List of all configuration keys
        """
        return list(self.config.options('DEFAULT'))

    def clear(self) -> None:
        """
        Clear all configuration settings.
        """
        self.config.clear()
        self._data_cache = None  # Clear cache

    def __len__(self) -> int:
        """
        Get the number of configuration settings.

        Returns:
            int: Number of configuration settings
        """
        return len(self.config.options('DEFAULT'))

    def __contains__(self, name: str) -> bool:
        """
        Check if a key exists in the configuration.

        Args:
            name: The key to check

        Returns:
            bool: True if key exists, False otherwise
        """
        return self.exists(name)

    def __getitem__(self, name: str) -> str:
        """
        Get a configuration value using dictionary syntax.

        Args:
            name: The key to look up

        Returns:
            str: The configuration value

        Raises:
            KeyError: If key is not found
        """
        value = self.get(name)
        if value is None:
            raise KeyError(f"Configuration '{name}' not found")
        return value

    def __setitem__(self, name: str, value: Union[str, int, float, bool]) -> None:
        """
        Set a configuration value using dictionary syntax.

        Args:
            name: The key to set
            value: The value to store
        """
        self.save(name, value)

    def items(self):
        """
        Get all key-value pairs in the configuration.

        Returns:
            ItemsView: View of all key-value pairs
        """
        return self.config.items('DEFAULT')
