# Configuration Manager Library

This Python library provides a simple and flexible way to manage
configuration settings using JSON, TOML, or INI/Unix-style configuration files.
It includes three main classes: `JSONSettings` for handling JSON-based
configurations, `TOMLSettings` for handling TOML-based configurations,
and `UnixSettings` for managing INI/Unix-style configuration files.

## Features

- **JSONSettings**:
  - Load, save, and manipulate key-value pairs in JSON files.
  - Automatic file creation with an empty JSON object if the file doesn't
    exist.
  - Support for nested key access using prefix-based filtering.
  - Dictionary-like access for ease of use.
  - Error handling with logging for file operations.

- **TOMLSettings**:
  - Load, save, and manipulate key-value pairs in TOML files.
  - Automatic file creation with an empty TOML file if the file doesn't
    exist.
  - Support for nested key access using prefix-based filtering.
  - Dictionary-like access for ease of use.
  - Error handling with logging for file operations.

- **UnixSettings**:
  - Manage `.cfg` or `.ini`-style configuration files using Python's
    `ConfigParser`.
  - Support for sections and case-sensitive keys.
  - Automatic wrapping of content in a `[DEFAULT]` section if no sections
    are present.
  - Dictionary-like access and prefix-based key filtering.
  - Configurable key-value separators and comment characters.

- Common features for all classes:
  - Methods for saving, retrieving, and removing key-value pairs.
  - Support for checking the existence of keys.
  - Logging for file operations and errors.
  - Type hints for better code clarity and IDE support.

## Installation

This library requires external dependencies for TOML support. To use it, include the package
in your project directory and install the required dependencies.

### Requirements

- Python 3.6 or higher
- Standard library modules: `json`, `logging`, `pathlib`, `configparser`, `io`
- External dependencies: `tomli`, `tomli-w`

## Usage

### JSONSettings Example

```python
from settings.json_settings import JSONSettings

# Initialize settings with a JSON file
settings = JSONSettings("config.json")

# Save a key-value pair
settings.save("username", "admin")
settings["theme"] = "dark"  # Dictionary-style access

# Write to file
settings.write()

# Retrieve a value
username = settings.get("username", "guest")
print(username)  # Output: admin

# Load all keys with a prefix
theme_settings = settings.loadAll("theme")
print(theme_settings)  # Output: {'': 'dark'}
```

### TOMLSettings Example

```python
from settings.toml_settings import TOMLSettings

# Initialize settings with a TOML file
settings = TOMLSettings("config.toml")

# Save a key-value pair
settings.save("username", "admin")
settings["theme"] = "dark"  # Dictionary-style access

# Write to file
settings.write()

# Retrieve a value
username = settings.get("username", "guest")
print(username)  # Output: admin

# Load all keys with a prefix
theme_settings = settings.loadAll("theme")
print(theme_settings)  # Output: {'': 'dark'}
```

### UnixSettings Example

```python
from settings.unix_settings import UnixSettings

# Initialize settings with an INI/CFG file
settings = UnixSettings("config.cfg", separator="=")

# Save a key-value pair in the DEFAULT section
settings.save("username", "admin")
settings["theme"] = "dark"  # Dictionary-style access

# Save a key-value pair in a custom section
settings.set("appearance", "font_size", 12)

# Write to file
settings.write()

# Retrieve a value
username = settings.get("username", "guest")
print(username)  # Output: admin

# Load all keys with a prefix
theme_settings = settings.loadAll("theme")
print(theme_settings)  # Output: {'': 'dark'}
```

## Project Structure

```()
settings/
├── __init__.py
├── json_settings.py
├── toml_settings.py
├── unix_settings.py
└── README.md
```

- `__init__.py`: Exports the `JSONSettings`, `TOMLSettings`, and `UnixSettings` classes.
- `json_settings.py`: Contains the `JSONSettings` class for JSON-based
  configuration management.
- `toml_settings.py`: Contains the `TOMLSettings` class for TOML-based
  configuration management.
- `unix_settings.py`: Contains the `UnixSettings` class for INI/Unix-style
  configuration management.

## API Reference

### JSONSettings

- `__init__(filepath: str | Path, auto_load: bool = True)`: Initialize with
  a JSON file path.
- `load(default: Optional[dict] = None) -> dict`: Load the JSON file into
  memory.
- `write(indent: int = 4) -> bool`: Write the configuration to the file.
- `save(name: str, value: Any) -> None`: Save a key-value pair.
- `remove(name: str) -> bool`: Remove a key.
- `exists(name: str) -> bool`: Check if a key exists.
- `get(name: str, default: Optional[Any] = None) -> Optional[Any]`: Retrieve
  a value.
- `loadAll(name: str, includeName: bool = False) -> Dict[str, str]`: Load
  keys with a given prefix.
- Dictionary-like access: `__getitem__`, `__setitem__`, `__contains__`.

### TOMLSettings

- `__init__(filepath: str | Path, auto_load: bool = True)`: Initialize with
  a TOML file path.
- `load(default: Optional[dict] = None) -> dict`: Load the TOML file into
  memory.
- `write() -> bool`: Write the configuration to the file.
- `save(name: str, value: Any) -> None`: Save a key-value pair.
- `remove(name: str) -> bool`: Remove a key.
- `exists(name: str) -> bool`: Check if a key exists.
- `get(name: str, default: Optional[Any] = None) -> Optional[Any]`: Retrieve
  a value.
- `loadAll(name: str, includeName: bool = False) -> Dict[str, str]`: Load
  keys with a given prefix.
- Dictionary-like access: `__getitem__`, `__setitem__`, `__contains__`.

### UnixSettings

- `__init__(filepath: str | Path, separator: str = "", comment: str = "#")`:
  Initialize with an INI/CFG file path.
- `load(default: Optional[dict] = None) -> dict`: Load the `[DEFAULT]`
  section into a dictionary.
- `write() -> bool`: Write the configuration to the file.
- `save(name: str, value: str | int | float | bool) -> None`: Save a
  key-value pair in the `[DEFAULT]` section.
- `set(section: str, name: str, value: str | int | float | bool) -> None`:
  Set a key-value pair in a specific section.
- `remove(name: str) -> bool`: Remove a key from the `[DEFAULT]` section.
- `exists(name: str) -> bool`: Check if a key exists in the `[DEFAULT]`
  section.
- `get(name: str, default: Optional[Any] = None) -> Optional[Any]`: Retrieve
  a value from the `[DEFAULT]` section.
- `loadAll(name: str, includeName: bool = False) -> Dict[str, str]`: Load
  keys with a given prefix from the `[DEFAULT]` section.
- `ensure_section(section: str) -> None`: Ensure a section exists.
- `has_section(section: str) -> bool`: Check if a section exists.
- `has_option(section: str, option: str) -> bool`: Check if an option
  exists in a section.
- Dictionary-like access: `__getitem__`, `__setitem__`, `__contains__`.
