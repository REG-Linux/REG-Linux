# REG-Linux ConfigGen

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Code style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Type checking: Pyright](https://img.shields.io/badge/type%20checker-pyright-blue)](https://github.com/microsoft/pyright)

**REG-Linux ConfigGen** is a Python-based configuration generator for the
REG-Linux retro gaming distribution. It dynamically generates emulator
configurations, handles controller mappings, manages video modes,
and orchestrates the launch of emulators with appropriate settings.

## Features

- **60+ Emulator Support** - Configuration generators for popular retro gaming
  emulators (libretro, DuckStation, PCSX2, Dolphin, MAME, and more)
- **Controller Mapping** - Native Python Evmapy implementation with zero file I/O,
  minimal latency (1ms), and support for multiple input devices
- **Special Input Devices** - Support for light guns, racing wheels, and other
  specialized controllers
- **Video Mode Management** - Dynamic resolution switching and display configuration
- **Bezel & HUD Support** - Automatic bezel generation with resize, tattoo, and
  gun borders support, plus MangoHUD integration
- **Metadata Integration** - Game metadata parsing and configuration
- **Custom Exceptions** - Hierarchical exception handling for better error management

## Architecture

### Module Structure (Refactored 2026)

```text
configgen/
├── emulatorlauncher.py    # DEPRECATED: Legacy entry point (delegates to launcher/)
├── core/                  # Core domain objects
│   ├── __init__.py
│   ├── command.py         # Command representation with env vars and arguments
│   ├── emulator.py        # Emulator configuration management
│   ├── emulator_config.py # Configuration loading utilities
│   └── exceptions.py      # Custom exception hierarchy (ConfigGenError, etc.)
├── factory/               # Generator factory pattern
│   ├── __init__.py
│   ├── generator_factory.py # Dynamic loading of emulator generators
│   └── mapping.py         # Emulator to generator mapping (60+ emulators)
├── launcher/              # Emulator launch orchestration
│   ├── __init__.py
│   ├── emulator_launcher.py # Main launcher (complete implementation, ~1300 lines)
│   ├── cleanup.py         # Resource cleanup management
│   ├── profiler.py        # Profiling utilities
│   └── hud_config.py      # HUD and bezel configuration helpers (getHudBezel, getHudConfig)
├── config/                # Configuration and paths
│   ├── __init__.py
│   ├── paths.py           # System path constants (formerly systemFiles.py)
│   └── settings_loader.py # Settings loading utilities
├── archives/              # Archive handling
│   ├── __init__.py
│   ├── squashfs.py        # SquashFS mount/unmount
│   └── zar.py             # ZAR archive mount/unmount
├── controllers/           # Controller management
│   ├── __init__.py
│   ├── controller.py      # Controller configuration
│   ├── controllerdb.py    # Controller database
│   ├── devices.py         # Device detection
│   ├── evmapy/            # Evmapy native implementation (refactored 2026)
│   │   ├── __init__.py
│   │   ├── event_handler.py # Native event processing with uinput
│   │   ├── manager.py     # High-level configuration loading
│   │   └── README.md      # Documentation and acknowledgments
│   ├── guns.py            # Light gun support
│   ├── metadata.py        # Game metadata
│   ├── mouse.py           # Mouse handling
│   └── utils/             # Controller utilities
│       ├── gunsUtils.py   # Gun precalibration
│       └── wheelsUtils.py # Wheel reconfiguration
├── video/                 # Video and compositor management
│   ├── __init__.py
│   ├── videoMode.py       # Video mode switching
│   └── windows_manager.py # Wayland/Sway compositor management
├── generators/            # Per-emulator configuration generators (60+)
│   ├── __init__.py
│   ├── generator.py       # Base Generator protocol/ABC
│   ├── libretro/          # RetroArch generator
│   ├── mame/              # MAME generator
│   ├── duckstation/       # PlayStation 1
│   ├── pcsx2/             # PlayStation 2
│   ├── dolphin/           # GameCube/Wii
│   └── ... (60+ emulators)
├── settings/              # Configuration file handlers
│   ├── __init__.py
│   ├── json_settings.py   # JSON configuration handler
│   ├── toml_settings.py   # TOML configuration handler
│   └── unix_settings.py   # Unix/INI configuration handler
├── bezel/                 # Bezel and overlay management
│   ├── __init__.py
│   ├── bezel_base.py      # Base bezel functionality
│   ├── bezel_common.py    # Common bezel utilities
│   ├── libretro_bezel_manager.py
│   └── mame_bezel_manager.py
├── client/                # REG-Linux integration
│   ├── __init__.py
│   └── regmsgclient.py    # ZeroMQ/Unix socket client
└── utils/                 # General utilities
    ├── __init__.py
    ├── logger.py          # Logging utilities
    ├── buildargs.py       # Argument building utilities
    └── systemServices.py  # System service integration
```

## Requirements

- **Python 3.12+** (required)
- **Linux** (tested on REG-Linux distribution)

### Core Dependencies

- `PyYAML` - YAML parsing and serialization
- `ruamel.yaml` - Advanced YAML handling with comment preservation
- `lxml` - XML processing for game metadata
- `Pillow` - Image processing for bezels/overlays
- `evdev` / `pyudev` - Linux input device handling
- `ffmpeg-python` - Media operations
- `requests` - HTTP client

## Installation

### Development Setup

```bash
# Clone the repository
cd /path/to/reglinux-configgen/configgen

# Create virtual environment (Python 3.12+ required)
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e .

# Install dev dependencies (optional, for development)
pip install -e ".[dev]"
```

### Production Installation

```bash
# Install via pip (when published)
pip install reglinux-configgen
```

## Usage

### Command-Line Interface

```bash
# Launch via entry point (legacy, delegates to new launcher)
reglinux-configgen [OPTIONS]

# Or run directly (legacy compatibility)
python -m configgen.emulatorlauncher [OPTIONS]
```

### Common Options

```bash
# Show help
reglinux-configgen --help

# Launch with system and ROM
reglinux-configgen -system snes -rom /path/to/rom.sfc \
  -p1index 0 -p1guid "030000005d040000192c000000000000" -p1name "Xbox Controller"

# Force specific emulator/core
reglinux-configgen -system psx -rom game.iso -emulator duckstation

# Netplay configuration
reglinux-configgen -system snes -rom game.sfc \
  -netplaymode client -netplayip 192.168.1.100 -netplayport 55435
```

### As a Library (New API)

```python
from configgen.launcher import launch_rom
from configgen.core import Emulator
from configgen.factory import getGenerator

# Load emulator configuration
emulator = Emulator("psx", "/path/to/game.iso")

# Get the appropriate generator
generator = getGenerator("duckstation")

# Generate the launch command
command = generator.generate(
    system=emulator,
    rom="/path/to/game.iso",
    players_controllers={},
    metadata={},
    guns=[],
    wheels=[],
    game_resolution={"width": 1920, "height": 1080},
)

# Execute the command
import subprocess

subprocess.run(command.array, env=command.env, cwd=command.cwd)
```

### Legacy API (Still Supported)

```python
from configgen.emulator import Emulator
from configgen.generators.duckstation.duckstationGenerator import DuckstationGenerator

# Load emulator configuration
emulator = Emulator("psx", "/path/to/game.iso")

# Generate configuration
generator = DuckstationGenerator()
command = generator.generate(
    system=emulator,
    rom="/path/to/game.iso",
    players_controllers={},
    metadata={},
    guns=[],
    wheels=[],
    game_resolution={},
)

# Execute the command
import subprocess

subprocess.run(command.command_args(), env=command.env)
```

## Development

### Code Quality Tools

```bash
# Linting with Ruff
ruff check configgen/

# Auto-fix with Ruff
ruff check --fix configgen/

# Format with Ruff
ruff format configgen/

# Type checking with Pyright
pyright configgen/
```

### Code Style

- **Formatter**: Ruff format (LF line endings, double quotes, preview mode)
- **Linter**: Ruff with standard Python rules (E, F, W, A, B, D, I, C4, PERF,
  PT, RET, SIM, TID, UP)
- **Type Checking**: Pyright in standard mode
- **Python Target**: 3.12

### Ignored Lint Rules

- `E203` - Whitespace before `:` (conflicts with formatter)
- `E501` - Line length (handled by formatter)
- `D100-D103, D107` - Missing docstrings (not enforced)
- `E402` - Module imports not at top (allowed for import fallbacks)
- `F811` - Redefinition (allowed in specific cases)

### Import Pattern

The project uses direct imports from the modular structure:

```python
from configgen.core import Command, Emulator
from configgen.factory import getGenerator
from configgen.config.paths import ROMS, SAVES
from configgen.launcher import launch_rom
from configgen.utils.logger import get_logger
```

Legacy imports are still supported via compatibility modules (deprecated).

### Generator Interface

All emulator generators must implement the `Generator` protocol:

```python
from typing import Any, Protocol
from configgen.emulator import Emulator
from configgen.command import Command


class Generator(Protocol):
    def generate(
        self,
        system: Emulator,
        rom: str,
        players_controllers: dict[str, Any],
        metadata: dict[str, Any],
        guns: list[Any],
        wheels: list[Any],
        game_resolution: dict[str, Any],
    ) -> Command:
        """Generate the command to launch the emulator."""
```

### Logging

Use the project's logger utility:

```python
from configgen.utils import get_logger

eslog = get_logger(__name__)

# Usage
eslog.debug("Debug message")
eslog.info("Info message")
eslog.warning("Warning message")
eslog.error("Error message")
```

## Advanced Features

### Profiling

To enable performance profiling:

```bash
# Create marker file
touch /var/run/emulatorlauncher.perf

# Run emulator (profile will be generated)
reglinux-configgen -system psx -rom game.iso

# After exit, profile data is at /var/run/emulatorlauncher.prof
# Convert to visual format:
gprof2dot.py -f pstats /var/run/emulatorlauncher.prof -o emulatorlauncher.dot
dot -Tpng emulatorlauncher.dot -o emulatorlauncher.png
```

### ZAR Archive Support

The configgen supports `.zar` and `.squashfs` archive mounting for compressed ROMs:

```python
from configgen.archives import zar, squashfs

# Mount ZAR archive
need_end, mountpoint, rom_path = zar.zar_begin("/path/to/archive.zar")

# Use rom_path...

# Unmount when done
if need_end and mountpoint:
    zar.zar_end(mountpoint)

# SquashFS support (same API)
need_end, mountpoint, rom_path = squashfs.squashfs_begin("/path/to/archive.squashfs")
```

### Compositor Management

Emulators requiring specific display servers (Wayland/X11) are handled automatically:

- Sway compositor for Wayland applications
- X11 fallback for legacy applications
- Automatic compositor cleanup on exit via `CleanupManager`

### Bezel & HUD Management

Full bezel and HUD support with automatic configuration:

```python
from configgen.launcher.emulator_launcher import getHudBezel, getHudConfig

# Get prepared bezel image (with resize, tattoo, gun borders)
bezel_path = getHudBezel(system, generator, rom, game_resolution, borders_size)

# Generate MangoHUD configuration string
hud_config = getHudConfig(
    system, system_name, emulator, core, rom, game_infos, bezel_path
)
```

### External Scripts

Pre/post launch script execution with security checks:

```python
from configgen.launcher.emulator_launcher import callExternalScripts

# Execute scripts for game start event
callExternalScripts(
    "/userdata/system/scripts", "gameStart", [system_name, emulator, core, rom_path]
)
```

### Cleanup Management

Automatic resource cleanup via `CleanupManager`:

```python
from configgen.launcher.cleanup import get_cleanup_manager

cleanup = get_cleanup_manager()

# Register resources for cleanup
cleanup.mark_rom_mounted(True, "/mnt/rom")
cleanup.mark_compositor_started()
cleanup.register_wheel_process(proc)
```

### Evmapy - Native Controller Mapping

Native Python implementation for controller-to-keyboard/mouse mapping:

```python
from configgen.controllers.evmapy import Evmapy

# Start evmapy (loads config from {emulator}_keys.py)
Evmapy.start(system, emulator, core, rom, players_controllers, guns)

# ... emulator runs with controller mapping ...

# Stop evmapy when done
Evmapy.stop()
```

**Key Features:**

- Zero file I/O: Configurations loaded from Python modules
- Minimal latency: 1ms event loop response time
- Thread-safe: Separate threads for event and mouse processing
- Light gun support: Dedicated mouse button mapping

For detailed documentation, see:
[`configgen/controllers/evmapy/README.md`](configgen/controllers/evmapy/README.md)

**Acknowledgments:** Based on the original [evmapy](https://github.com/kempniu/evmapy) project.

### Cleanup Management (Continued)

```python
# Cleanup all resources
import asyncio

asyncio.run(cleanup.cleanup_all())
```

## Supported Emulators

The following emulators have dedicated configuration generators:

| Category         | Emulators                                                                   |
| ---------------- | --------------------------------------------------------------------------- |
| **Multi-system** | libretro (RetroArch), MAME, FinalBurn Neo                                   |
| **PlayStation**  | DuckStation, PCSX2, ePSXE, Beetle PSX                                       |
| **Nintendo**     | Dolphin (GC/Wii), Cemu (Wii U), Citra (3DS), Yuzu (Switch), Snes9x, Gens/GS |
| **Sega**         | Flycast (Dreamcast), Redream, Genesis Plus GX                               |
| **PC Engine**    | Mednafen, Beetle PCE                                                        |
| **Handheld**     | PPSSPP (PSP), MelonDS (DS), DeSmuME (DS), Vita3K                            |
| **Computer**     | Amiberry (Amiga), Hatari (Atari ST), DOSBox, ScummVM                        |
| **Arcade**       | MAME, FinalBurn Neo, Flycast                                                |
| **Other**        | Xemu (Xbox), Redream, RPCS3 (PS3)                                           |

## Troubleshooting

### Common Issues

**Controller not detected:**

- Ensure Evmapy is properly configured
- Check that controller is recognized by `evtest`
- Verify udev rules are installed

**Video mode switching fails:**

- Ensure `xrandr` or `wlr-randr` is available
- Check display server compatibility (X11 vs Wayland)

**Emulator crashes on launch:**

- Check emulator-specific configuration in `generators/`
- Verify BIOS files are in correct location (`/userdata/bios/`)
- Review logs at `/var/log/reglinux/`

### Debug Mode

Enable verbose logging for troubleshooting:

```bash
reglinux-configgen --verbose --debug
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Make your changes
4. Run tests and linting (`ruff check .`, `pyright .`)
5. Commit your changes (`git commit -m 'Add my feature'`)
6. Push to the branch (`git push origin feature/my-feature`)
7. Open a Pull Request

## Refactoring History

### 2026 Refactoring

The project underwent a major refactoring in 2026 to improve modularity and maintainability:

#### Phase 1: Modularization

- **Before**: Monolithic `emulatorlauncher.py` (1471 lines), flat structure
- **After**: Modular structure with clear separation of concerns

Key changes:

1. Extracted domain objects to `core/`
2. Created factory pattern for generator loading
3. Split launcher into phased execution with cleanup management
4. Moved utilities to dedicated modules (`archives/`, `video/`, `controllers/utils/`)
5. Centralized path constants in `config/paths.py`

#### Phase 2: Launcher Consolidation (Latest)

- **Problem**: Functionality split between `emulatorlauncher.py` (legacy) and `launcher/emulator_launcher.py` (incomplete)
- **Solution**: Consolidated all launch functionality in `launcher/emulator_launcher.py`

Key changes:

1. Migrated complete launch logic to `launcher/emulator_launcher.py` (~1300 lines)
   - `getHudBezel()` - Bezel preparation with resize, tattoo, gun borders
   - `extractGameInfosFromXml()` - XML metadata parsing
   - `callExternalScripts()` - External script execution with security checks
   - `getHudConfig()` - MangoHUD configuration string generation
   - `runCommand()` - Subprocess execution with timeout and error handling
   - `_configure_hud()` - Complete HUD configuration
   - `_cleanup_system()` - Video mode and mouse restoration
2. Reduced `emulatorlauncher.py` to a thin delegation layer (~165 lines)
3. Fixed type annotations for `guns` and `wheels` parameters
   (`dict[str, Any] | list[Any]`)
4. Added proper type safety with Pyright validation (0 errors, 0 warnings)
5. Maintained backward compatibility for CLI entry point

#### Phase 3: Error Handling & Type Modernization (2026)

**Custom Exception Hierarchy:**

- Created `configgen/core/exceptions.py` with 10 specialized exception types:
  - `ConfigGenError` (base exception)
  - `EmulatorNotFoundError` - No emulator configuration found
  - `ArchiveMountError` - Archive mount/unmount failures
  - `BIOSNotFoundError` - Missing BIOS files
  - `MachineNotFoundError` - Missing machine configurations
  - `GeneratorError` - Generator configuration errors
  - `FileMissingError` - Required files not found
  - `ImageProcessingError` - Image operation failures
  - `TattooImageError` - Tattoo processing errors
  - `BezelImageError` - Bezel processing errors
  - `ExternalScriptError` - External script failures

**Bezel Fix:**

- Fixed `getHudBezel()` in `launcher/hud_config.py` to properly resize bezels
- Added aspect ratio validation before applying bezels
- Ensured bezel dimensions match screen resolution
- Added proper error handling for bezel operations

**Type Hint Modernization:**

- Updated `controllers/controller.py` to use Python 3.12+ type hints
- Replaced `Optional[X]` with `X | None` syntax
- Added `from __future__ import annotations` for forward references

### Code Quality Improvements

- **Type Safety**: All functions now have proper type annotations
- **Linting**: Ruff check passes with 0 errors
- **Formatting**: Ruff format applied consistently
- **Type Checking**: Pyright validation passes with 0 errors, 0 warnings
- **Exception Handling**: All generic `Exception` replaced with specific types
- **Documentation**: All comments and docstrings in English (en-US)

## License

This project is part of the REG-Linux distribution. See the main repository for
licensing information.

## Acknowledgments

- **EmulationStation** - Frontend integration
- **Evmapy** - Controller mapping
  - Original evmapy project by [kempniu](https://github.com/kempniu/evmapy)
  - Our native Python implementation adapts and extends the original concepts
- **RetroArch** - libretro core support
- **All emulator developers** - For their outstanding work

## Links

- [REG-Linux Main Repository](#)
- [EmulationStation](https://emulationstation.org/)
- [RetroArch](https://www.retroarch.com/)
