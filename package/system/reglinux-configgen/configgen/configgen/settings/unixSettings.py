#!/usr/bin/env python3

import configparser
import os
import re
import io
import tempfile
from pathlib import Path
from functools import lru_cache
from typing import Any, Dict, Optional, Union

from configgen.utils.logger import get_logger

eslog = get_logger(__name__)
__source__ = os.path.basename(__file__)


class UnixSettings:
    """
    A class for reading, modifying, and writing INI-style configuration files
    using a simplified flat structure (without explicit use of sections).

    This version includes atomic writing to prevent file corruption,
    pathlib usage for path manipulation, and regex caching for better performance.

    Attributes:
        settingsFile (Path): Path to the configuration file
        separator (str): Optional separator between keys and values in output file
        encoding (str): Text encoding used for reading and writing the file
        config (ConfigParser): Internal ConfigParser instance
        _regex_cache (dict): Cache for compiled regular expressions
    """

    def __init__(
        self,
        settingsFile: Union[str, Path],
        separator: str = '',
        encoding: str = 'utf-8-sig'
    ):
        """
        Initialize a UnixSettings instance.

        Args:
            settingsFile (Union[str, Path]): Path to the configuration file.
            separator (str): Optional separator between keys and values in output file.
            encoding (str): The encoding to use for reading and writing the file.
        """
        self.settingsFile = Path(settingsFile)
        self.separator = separator
        self.encoding = encoding

        # Use ConfigParser without interpolation and preserve key case
        eslog.debug(f"Creating parser for {self.settingsFile}")
        self.config = configparser.ConfigParser(interpolation=None, strict=False)
        self.config.optionxform = lambda optionstr: optionstr  # Preserve original case of keys
        self._regex_cache = {}

        if self.settingsFile.exists():
            try:
                # Read file content as if it belongs to a [DEFAULT] section
                content = self.settingsFile.read_text(encoding=self.encoding)
                fake_file = io.StringIO('[DEFAULT]\n' + content)
                self.config.read_file(fake_file)
            except (IOError, UnicodeDecodeError) as e:
                eslog.error(f"Failed to read {self.settingsFile}: {e}")
        else:
            eslog.warning(f"Configuration file not found. A new blank file will be created: {self.settingsFile}")

    def write(self) -> bool:
        """
        Write all settings from the DEFAULT section back to the original file
        atomically to prevent data corruption.

        Creates a temporary file and renames it, ensuring the original file
        is not destroyed if an error occurs during writing.

        Returns:
            bool: True if writing was successful, False otherwise.
        """
        temp_path = None
        try:
            # Write to a temporary file in the same directory
            with tempfile.NamedTemporaryFile('w', encoding='utf-8', delete=False,
                                             dir=self.settingsFile.parent) as tmp_file:
                temp_path = Path(tmp_file.name)
                # Write each key-value pair with the specified separator
                for key, value in self.config.items('DEFAULT'):
                    tmp_file.write(f"{key}{self.separator}={self.separator}{value}\n")

            # Rename temporary file to original (atomic operation)
            os.rename(temp_path, self.settingsFile)
            eslog.debug(f"Settings successfully saved to {self.settingsFile}")
            return True
        except (IOError, OSError) as e:
            eslog.error(f"Error writing settings to {self.settingsFile}: {e}")
            # If renaming fails, remove the temporary file
            if temp_path is not None and temp_path.exists():
                temp_path.unlink()
            return False

    def save(self, name: str, value: Any):
        """
        Save a setting to the DEFAULT section.

        Args:
            name (str): The key name.
            value (Any): The value to set (will be converted to string).
        """
        # Mask password values in logs for security
        log_value = "********" if "password" in name.lower() else value
        eslog.debug(f"Setting {name} = {log_value} in {self.settingsFile}")
        self.config.set('DEFAULT', name, str(value))

    def disableAll(self, name_prefix: str):
        """
        Remove all settings whose keys start with the given prefix.

        Args:
            name_prefix (str): Prefix to match keys against.
        """
        eslog.debug(f"Disabling all settings starting with '{name_prefix}' in {self.settingsFile}")
        # Iterate over a copy of the keys list to allow removal during iteration
        keys_to_remove = [key for key in self.config['DEFAULT'] if key.startswith(name_prefix)]
        for key in keys_to_remove:
            self.config.remove_option('DEFAULT', key)

    def remove(self, name: str):
        """
        Remove a single setting from the DEFAULT section.

        Args:
            name (str): The key to remove.
        """
        self.config.remove_option('DEFAULT', name)

    @staticmethod
    @lru_cache(maxsize=128)
    def protectString(s: str) -> str:
        """
        Sanitize a string by replacing non-alphanumeric characters with underscores.
        Uses caching to optimize repeated calls with the same string.

        Args:
            s (str): The input string.

        Returns:
            str: A safe version of the string for use as a key.
        """
        return re.sub(r'[^A-Za-z0-9\-\.]+', '_', s)

    def loadAll(self, name: str, includeName: bool = False) -> Dict[str, str]:
        """
        Load all settings with keys that match the given prefix.

        Args:
            name (str): The prefix to match (e.g., "core").
            includeName (bool): Whether to include the prefix in returned keys.

        Returns:
            Dict[str, str]: Dictionary of matching key-value pairs.
        """
        eslog.debug(f"Searching for keys with prefix '{name}.' in {self.settingsFile}")

        # Optimization: compile and cache the regular expression
        safe_prefix = self.protectString(name)
        if safe_prefix not in self._regex_cache:
            self._regex_cache[safe_prefix] = re.compile(rf"^{re.escape(safe_prefix)}\.(.+)")

        compiled_regex = self._regex_cache[safe_prefix]

        result = {}
        for key, value in self.config.items('DEFAULT'):
            match = compiled_regex.match(key)
            if match:
                if includeName:
                    # Use the original key to maintain format
                    result[key] = value
                else:
                    # Use only the suffix after the prefix
                    result[match.group(1)] = value
        return result
