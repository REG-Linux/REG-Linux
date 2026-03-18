# Evmapy - Controller Input Mapping for REG-Linux

Native Python implementation for mapping gamepad/controller inputs to keyboard/mouse events in the REG-Linux retro gaming distribution.

## Acknowledgments

This implementation is based on the original **evmapy** project by [kempniu](https://github.com/kempniu/evmapy).

We would like to express our gratitude to the original author and contributors for:

- Pioneering the controller-to-keyboard mapping concept for retro gaming
- Providing the foundational architecture and design patterns
- Establishing the configuration file format (.keys files)
- Creating the trigger/action system that powers input mapping

This native Python implementation adapts and extends the original concepts with:

- Zero file I/O configuration loading
- Optimized event processing with minimal latency
- Integration with the REG-Linux ConfigGen ecosystem

**Original Project:** <https://github.com/kempniu/evmapy>

---

Evmapy enables controllers to work with games that expect keyboard input by:

- Mapping controller buttons to keyboard keys
- Converting analog sticks to mouse movement
- Supporting light guns and special input devices
- Loading configurations from emulator-specific modules

## Architecture

```text
evmapy/
├── __init__.py          # Package exports (Evmapy, EvmapyNative)
├── manager.py           # High-level API (Evmapy class)
└── event_handler.py     # Low-level event processing (EvmapyNative class)
```

### Components

#### `Evmapy` (Manager.py)

High-level manager for configuration and lifecycle:

- Loads configurations from `{emulator}_keys.py` modules
- Prepares device configurations as dictionaries
- Manages the native event handler lifecycle

#### `EvmapyNative` (Event_handler.py)

Low-level event processing engine:

- Monitors input devices via `evdev`
- Processes button presses, axis movements, and hat switches
- Injects keyboard/mouse events via `uinput`
- Runs in background threads for non-blocking operation

## Usage

### Basic Example

```python
from configgen.controllers.evmapy import Evmapy

# Start evmapy with configuration
Evmapy.start(
    system=emulator_system,
    emulator="pcsx2",
    core="pcsx2",
    rom="/path/to/game.iso",
    players_controllers={1: player1_controller},
    guns=[]
)

# ... emulator runs with controller mapping ...

# Stop evmapy when done
Evmapy.stop()
```

### Configuration Modules

Each emulator provides its own configuration module:

```python
# configgen/generators/pcsx2/pcsx2_keys.py
from typing import Any

ACTIONS_PLAYER1: list[dict[str, Any]] = [
    # Standard buttons
    {"trigger": "cross", "type": "key", "target": "KEY_ENTER"},
    {"trigger": "circle", "type": "key", "target": "KEY_BACKSPACE"},

    # D-pad
    {"trigger": "up", "type": "key", "target": "KEY_UP"},
    {"trigger": "down", "type": "key", "target": "KEY_DOWN"},

    # Analog stick as mouse
    {"trigger": "joystick1", "type": "mouse"},

    # Hotkey combinations
    {
        "trigger": ["hotkey", "start"],
        "type": "key",
        "target": ["KEY_LEFTALT", "KEY_F4"]
    },
]

CONFIG: dict[str, Any] = {
    "actions_player1": ACTIONS_PLAYER1,
}

def get_config() -> dict[str, Any]:
    return CONFIG
```

## Configuration Format

### Action Types

| Type    | Description                | Target Format                         |
| ------- | -------------------------- | ------------------------------------- |
| `key`   | Inject keyboard key(s)     | `"KEY_ENTER"` or `["KEY_A", "KEY_B"]` |
| `mouse` | Map axis to mouse movement | `"X"` or `"Y"`                        |
| `exec`  | Execute shell command      | `"/path/to/script.sh"`                |

### Trigger Modes

| Mode            | Description                          |
| --------------- | ------------------------------------ |
| `all` (default) | All triggers must be active          |
| `any`           | Any trigger activates the action     |
| `sequence`      | Triggers must be pressed in sequence |

### Example Configurations

**Button Mapping:**

```json
{
  "trigger": "cross",
  "type": "key",
  "target": "KEY_ENTER"
}
```

**Hotkey Combination:**

```json
{
  "trigger": ["hotkey", "x"],
  "type": "key",
  "target": ["KEY_LEFTSHIFT", "KEY_F1"],
  "mode": "all"
}
```

**Analog Stick as Mouse:**

```json
{
  "trigger": "joystick1",
  "type": "mouse",
  "target": "X"
}
```

**Sequence Trigger:**

```json
{
  "trigger": ["up", "down", "left", "right"],
  "type": "exec",
  "target": "/usr/bin/cheat_code.sh",
  "mode": "sequence"
}
```

## Technical Details

### Performance Optimizations

- **Zero file I/O**: Configurations loaded directly from Python modules
- **`__slots__`**: All dataclasses use `__slots__` for reduced memory
- **Cached ecodes**: Pre-computed keyboard code lookups
- **Minimal allocations**: Event loop avoids runtime allocations
- **1ms latency**: Select timeout optimized for responsiveness

### Thread Architecture

```text
Main Thread          Event Thread        Mouse Thread
    |                    |                    |
    |--- start() ------> |                    |
    |                    |--- event_loop() ---|
    |                    |                    |--- mouse_loop()
    |                    |                    |
    |--- stop() ------> | (join threads)     |
```

### Input Processing Flow

1. **Device Discovery**: `evdev.list_devices()` finds all input devices
2. **Configuration Loading**: `{emulator}_keys.py` provides mappings
3. **Event Monitoring**: `select()` monitors device file descriptors
4. **State Tracking**: Button/axis states updated on each event
5. **Action Execution**: Matching actions trigger key/mouse events
6. **Event Injection**: `uinput` injects events into the system

## Supported Input Types

| Input Type  | Linux Event | Description                   |
| ----------- | ----------- | ----------------------------- |
| Buttons     | `EV_KEY`    | Digital button press/release  |
| Analog Axes | `EV_ABS`    | Analog stick/trigger position |
| D-pad (Hat) | `EV_ABS`    | Hat switch X/Y values         |
| Mouse       | `EV_REL`    | Relative mouse movement       |

## Light Gun Support

Evmapy supports light gun devices with mouse button mapping:

```python
guns = [
    {
        "node": "/dev/input/event5",
        "buttons": ["left", "right", "middle"]
    }
]

# Configuration
CONFIG = {
    "actions_gun1": [
        {"trigger": "left", "type": "key", "target": "KEY_LEFTMOUSE"},
    ]
}
```

## API Reference

### `Evmapy.start()`

```python
@staticmethod
def start(
    system: Any,
    emulator: str,
    core: str,
    rom: str,
    players_controllers: dict[str, Any],
    guns: dict[str, Any] | list[dict[str, Any]],
) -> None
```

Start the evmapy event mapping system.

### `Evmapy.stop()`

```python
@staticmethod
def stop() -> None
```

Stop evmapy and release all resources.

### `EvmapyNative.load_config_dict()`

```python
def load_config_dict(
    device_name: str,
    config_data: dict[str, Any],
) -> bool
```

Load device configuration from dictionary (no file I/O).

## Troubleshooting

### Controllers Not Working

1. Check that `{emulator}_keys.py` exists and has `get_config()`
2. Verify controller is detected: `ls /dev/input/event*`
3. Check logs: `journalctl -f | grep evmapy`

### High CPU Usage

1. Ensure using native implementation (not external evmapy)
2. Check for excessive mouse actions (use deadzones)
3. Verify event loop is running (should be <1% CPU)

### Permission Denied

Evmapy requires access to `/dev/input/event*` devices:

```bash
# Add user to input group
sudo usermod -aG input $USER

# Or set udev rules
sudo tee /etc/udev/rules.d/99-evmapy.rules <<EOF
KERNEL=="event*", SUBSYSTEM=="input", MODE="0660", GROUP="input"
EOF
```

## Development

### Adding Support for New Emulator

1. Create `configgen/generators/{emulator}/{emulator}_keys.py`
2. Define `ACTIONS_PLAYER1` with button mappings
3. Implement `get_config()` function
4. Test with emulator launch

### Testing

```python
# Test configuration loading
from configgen.generators.pcsx2.pcsx2_keys import get_config
config = get_config()
assert "actions_player1" in config

# Test event handler
from configgen.controllers.evmapy import EvmapyNative
native = EvmapyNative()
native.load_config_dict("event0", config)
```

## License

Part of REG-Linux ConfigGen distribution.
