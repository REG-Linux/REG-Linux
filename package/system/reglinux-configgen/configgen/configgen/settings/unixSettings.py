#!/usr/bin/env python3

import configparser
import os
import re
import io
from configgen.utils.logger import get_logger

eslog = get_logger(__name__)
__source__ = os.path.basename(__file__)


class UnixSettings:
    """
    A class for reading, modifying, and writing INI-style configuration files
    using a simplified flat structure (without explicit section usage).
    """

    def __init__(self, settingsFile, separator='', defaultComment='#'):
        """
        Initialize a UnixSettings instance.

        Args:
            settingsFile (str): Path to the settings file.
            separator (str): Optional separator between keys and values in the output file.
            defaultComment (str): Placeholder for compatibility, not used.
        """
        self.settingsFile = settingsFile
        self.separator = separator
        self.comment = defaultComment  # Unused; kept for backward compatibility.

        # Use ConfigParser without interpolation and preserve key case
        eslog.debug(f"Creating parser for {self.settingsFile}")
        self.config = configparser.ConfigParser(interpolation=None, strict=False)
        self.config.optionxform = str

        try:
            # Read file contents as if they belonged to a [DEFAULT] section
            with open(self.settingsFile, encoding='utf_8_sig') as f:
                content = f.read()
            fake_file = io.StringIO('[DEFAULT]\n' + content)
            self.config.read_file(fake_file)
        except IOError as e:
            eslog.error(f"Failed to read {self.settingsFile}: {str(e)}")

    def write(self):
        """
        Write all settings in the DEFAULT section back to the original file.
        """
        try:
            with open(self.settingsFile, 'w', encoding='utf-8') as fp:
                for key, value in self.config.items('DEFAULT'):
                    # Write as key<separator>=<separator>value (e.g., with sep=' ', "key = value")
                    fp.write(f"{key}{self.separator}={self.separator}{value}\n")
        except Exception as e:
            eslog.error(f"Error writing settings to {self.settingsFile}: {str(e)}")

    def save(self, name, value):
        """
        Save a setting to the DEFAULT section.

        Args:
            name (str): The key name.
            value (Any): The value to set.
        """
        if "password" in name.lower():
            eslog.debug(f"Writing {name} = ******** to {self.settingsFile}")
        else:
            eslog.debug(f"Writing {name} = {value} to {self.settingsFile}")
        self.config.set('DEFAULT', name, str(value))

    def disableAll(self, name_prefix):
        """
        Remove all settings whose keys start with the given prefix.

        Args:
            name_prefix (str): Prefix to match keys.
        """
        eslog.debug(f"Disabling all settings starting with '{name_prefix}' in {self.settingsFile}")
        for key, _ in list(self.config.items('DEFAULT')):
            if key.startswith(name_prefix):
                self.config.remove_option('DEFAULT', key)

    def remove(self, name):
        """
        Remove a single setting from the DEFAULT section.

        Args:
            name (str): The key to remove.
        """
        self.config.remove_option('DEFAULT', name)

    @staticmethod
    def protectString(s):
        """
        Sanitize a string by replacing non-alphanumeric characters with underscores.

        Args:
            s (str): The input string.

        Returns:
            str: A safe version of the string for use as a key.
        """
        return re.sub(r'[^A-Za-z0-9\-\.]+', '_', s)

    def loadAll(self, name, includeName=False):
        """
        Load all settings with keys that match the given prefix (e.g., "core.").

        Args:
            name (str): The prefix to match (e.g., "core").
            includeName (bool): Whether to include the prefix in the returned keys.

        Returns:
            dict: Matching key-value pairs.
        """
        eslog.debug(f"Looking for keys with prefix '{name}.' in {self.settingsFile}")
        result = {}
        for key, value in self.config.items('DEFAULT'):
            match = re.match(rf"^{self.protectString(name)}\.(.+)", self.protectString(key))
            if match:
                if includeName:
                    result[f"{name}.{match.group(1)}"] = value
                else:
                    result[match.group(1)] = value
        return result
