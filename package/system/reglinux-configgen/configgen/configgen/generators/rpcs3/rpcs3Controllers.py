from os import makedirs, path
from typing import Any

from configgen.utils.logger import get_logger

from .rpcs3Config import RPCS3_INPUT_DIR

eslog = get_logger(__name__)

# Sony controller GUIDs for DS3, DS4, and DS5
VALID_SONY_GUIDS = [
    # ds3
    "030000004c0500006802000011010000",
    "030000004c0500006802000011810000",
    "050000004c0500006802000000800000",
    "050000004c0500006802000000000000",
    # ds4
    "030000004c050000c405000011810000",
    "050000004c050000c405000000810000",
    "030000004c050000cc09000011010000",
    "050000004c050000cc09000000010000",
    "030000004c050000cc09000011810000",
    "050000004c050000cc09000000810000",
    "030000004c050000a00b000011010000",
    "030000004c050000a00b000011810000",
    # ds5
    "030000004c050000e60c000011810000",
    "050000004c050000e60c000000810000",
]

# Input mapping from generic names to RPCS3 configuration names
INPUT_MAPPING = [
    ("up", "Up", [("BTN_DPAD_UP", "D-Pad Up"), ("ABS_HAT0Y", "Hat0 Y-")]),
    ("down", "Down", [("BTN_DPAD_DOWN", "D-Pad Down"), ("ABS_HAT0Y", "Hat0 Y+")]),
    ("left", "Left", [("BTN_DPAD_LEFT", "D-Pad Left"), ("ABS_HAT0X", "Hat0 X-")]),
    ("right", "Right", [("BTN_DPAD_RIGHT", "D-Pad Right"), ("ABS_HAT0X", "Hat0 X+")]),
    ("l2", "L2", [("BTN_TL2", "TL 2"), ("ABS_Z", "LZ+")]),
    ("r2", "R2", [("BTN_TR2", "TR 2"), ("ABS_RZ", "RZ+")]),
    ("a", "Cross", [("BTN_A", "A")]),
    ("b", "Circle", [("BTN_B", "B")]),
    ("x", "Square", [("BTN_X", "X")]),
    ("y", "Triangle", [("BTN_Y", "Y")]),
    ("joystick1up", "Left Stick Up", [("ABS_Y", "LY-")]),
    ("joystick1left", "Left Stick Left", [("ABS_X", "LX-")]),
    ("joystick2up", "Right Stick Up", [("ABS_RY", "RY-")]),
    ("joystick2left", "Right Stick Left", [("ABS_RX", "RX-")]),
]


def generateControllerConfig(system: Any, controllers: Any, rom: str) -> None:
    if not path.isdir(RPCS3_INPUT_DIR):
        makedirs(RPCS3_INPUT_DIR)

    # Create mapping dictionary from input mapping list
    mapping_dict = {}
    for input_name, config_name, event_variations in INPUT_MAPPING:
        mapping_dict[input_name] = {
            "config_name": config_name,
            "event_variations": event_variations,
        }

    nplayer, ds3player, ds4player, dsplayer = 1, 1, 1, 1
    controller_counts = {}

    configFileName = f"{RPCS3_INPUT_DIR}/Default.yml"
    with open(configFileName, "w", encoding="utf_8_sig") as f:
        for _, pad in sorted(controllers.items()):
            if nplayer <= 7:
                eslog.debug(f"Controller #{nplayer} - {pad.guid}")

                # Check for DualShock / DualSense
                if (
                    pad.guid in VALID_SONY_GUIDS
                    and f"rpcs3_controller{nplayer}" in system.config
                    and system.config[f"rpcs3_controller{nplayer}"] == "Sony"
                ):
                    eslog.debug("*** Using DualShock / DualSense configuration ***")
                    configure_sony_controller(
                        f,
                        pad,
                        nplayer,
                        VALID_SONY_GUIDS,
                        ds3player,
                        ds4player,
                        dsplayer,
                    )

                    # Update player counters for Sony controllers
                    if pad.guid in VALID_SONY_GUIDS[:4]:  # DS3
                        ds3player += 1
                    elif pad.guid in VALID_SONY_GUIDS[4:12]:  # DS4
                        ds4player += 1
                    else:  # DS5
                        dsplayer += 1
                elif (
                    f"rpcs3_controller{nplayer}" in system.config
                    and system.config[f"rpcs3_controller{nplayer}"] == "Evdev"
                ):
                    eslog.debug("*** Using EVDEV configuration ***")
                    configure_evdev_controller(f, pad, nplayer, mapping_dict)
                else:
                    eslog.debug("*** Using default SDL2 configuration ***")
                    configure_sdl_controller(f, pad, nplayer, controller_counts)

                nplayer += 1


def configure_sony_controller(
    f: Any,
    pad: Any,
    nplayer: int,
    valid_sony_guids: Any,
    ds3player: int,
    ds4player: int,
    dsplayer: int,
) -> None:
    """Configure Sony controllers (DS3, DS4, DS5)"""
    f.write(f"Player {nplayer} Input:\n")

    # Determine controller type and increment appropriate counter
    if pad.guid in valid_sony_guids[:4]:  # DS3
        f.write("  Handler: DualShock 3\n")
        f.write(f'  Device: "DS3 Pad #{ds3player}"\n')
    elif pad.guid in valid_sony_guids[4:12]:  # DS4
        f.write("  Handler: DualShock 4\n")
        f.write(f'  Device: "DS4 Pad #{ds4player}"\n')
    else:  # DS5
        f.write("  Handler: DualSense\n")
        f.write(f'  Device: "DualSense Pad #{dsplayer}"\n')

    # Write standard Sony controller configuration
    f.write("  Config:\n")
    sony_config_lines = [
        "    Left Stick Left: LS X-",
        "    Left Stick Down: LS Y-",
        "    Left Stick Right: LS X+",
        "    Left Stick Up: LS Y+",
        "    Right Stick Left: RS X-",
        "    Right Stick Down: RS Y-",
        "    Right Stick Right: RS X+",
        "    Right Stick Up: RS Y+",
        "    Start: Options",
        "    Select: Share",
        "    PS Button: PS Button",
        "    Square: Square",
        "    Cross: Cross",
        "    Circle: Circle",
        "    Triangle: Triangle",
        "    Left: Left",
        "    Down: Down",
        "    Right: Right",
        "    Up: Up",
        "    R1: R1",
        "    R2: R2",
        "    R3: R3",
        "    L1: L1",
        "    L2: L2",
        "    L3: L3",
        "    Motion Sensor X:",
        '      Axis: ""',
        "      Mirrored: false",
        "      Shift: 0",
        "    Motion Sensor Y:",
        '      Axis: ""',
        "      Mirrored: false",
        "      Shift: 0",
        "    Motion Sensor Z:",
        '      Axis: ""',
        "      Mirrored: false",
        "      Shift: 0",
        "    Motion Sensor G:",
        '      Axis: ""',
        "      Mirrored: false",
        "      Shift: 0",
        '    Pressure Intensity Button: ""',
        "    Pressure Intensity Percent: 50",
        "    Pressure Intensity Toggle Mode: false",
        "    Left Stick Multiplier: 100",
        "    Right Stick Multiplier: 100",
        "    Left Stick Deadzone: 40",
        "    Right Stick Deadzone: 40",
        "    Left Trigger Threshold: 0",
        "    Right Trigger Threshold: 0",
        "    Left Pad Squircling Factor: 8000",
        "    Right Pad Squircling Factor: 8000",
        "    Color Value R: 0",
        "    Color Value G: 0",
        "    Color Value B: 20",
        "    Blink LED when battery is below 20%: true",
        "    Use LED as a battery indicator: false",
        "    LED battery indicator brightness: 10",
        "    Player LED enabled: true",
        "    Enable Large Vibration Motor: true",
        "    Enable Small Vibration Motor: true",
        "    Switch Vibration Motors: false",
        "    Mouse Movement Mode: Relative",
        "    Mouse Deadzone X Axis: 60",
        "    Mouse Deadzone Y Axis: 60",
        "    Mouse Acceleration X Axis: 200",
        "    Mouse Acceleration Y Axis: 250",
        "    Left Stick Lerp Factor: 100",
        "    Right Stick Lerp Factor: 100",
        "    Analog Button Lerp Factor: 100",
        "    Trigger Lerp Factor: 100",
        "    Device Class Type: 0",
        "    Vendor ID: 1356",
        "    Product ID: 616",
        '  Buddy Device: ""',
    ]

    for line in sony_config_lines:
        f.write(f"{line}\n")


def configure_evdev_controller(
    f: Any, pad: Any, nplayer: int, mapping_dict: Any
) -> None:
    """Configure EVDEV controllers"""
    f.write(f"Player {nplayer} Input:\n")
    f.write("  Handler: Evdev\n")
    f.write(f"  Device: {pad.dev}\n")
    f.write("  Config:\n")
    f.write("    Start: Start\n")
    f.write("    Select: Select\n")
    f.write("    PS Button: Mode\n")

    # Map inputs based on the mapping dictionary
    for inputIdx in pad.inputs:
        input = pad.inputs[inputIdx]
        if input.name in mapping_dict:
            config_name = mapping_dict[input.name]["config_name"]
            event_variations = mapping_dict[input.name]["event_variations"]
            for event_type, value_name in event_variations:
                if (
                    "BTN" in event_type
                    and input.type == "button"
                    or "HAT" in event_type
                    and input.type == "hat"
                ):
                    f.write(f"    {config_name}: {value_name}\n")
                elif "ABS" in event_type and input.type == "axis":
                    # Handle axis for sticks
                    if config_name == "Left Stick Up":
                        f.write(f"    {config_name}: {value_name}\n")
                        # Write the down values also
                        f.write("    Left Stick Down: LY+\n")
                    elif config_name == "Left Stick Left":
                        f.write(f"    {config_name}: {value_name}\n")
                        # Write the right values also
                        f.write("    Left Stick Right: LX+\n")
                    # Handle right stick axes
                    elif config_name == "Right Stick Up":
                        f.write(f"    {config_name}: {value_name}\n")
                        # Write the down values
                        f.write("    Right Stick Down: RY+\n")
                    elif config_name == "Right Stick Left":
                        f.write(f"    {config_name}: {value_name}\n")
                        # Write the right values
                        f.write("    Right Stick Right: RX+\n")
                    else:
                        f.write(f"    {config_name}: {value_name}\n")

    # Continue with default EVDEV settings
    evdev_config_lines = [
        "    R1: TR",
        "    R3: Thumb R",
        "    L1: TL",
        "    L3: Thumb L",
        "    Motion Sensor X:",
        "      Axis: X",
        "      Mirrored: false",
        "      Shift: 0",
        "    Motion Sensor Y:",
        "      Axis: Y",
        "      Mirrored: false",
        "      Shift: 0",
        "    Motion Sensor Z:",
        "      Axis: Z",
        "      Mirrored: false",
        "      Shift: 0",
        "    Motion Sensor G:",
        "      Axis: RY",
        "      Mirrored: false",
        "      Shift: 0",
        '    Pressure Intensity Button: ""',
        "    Pressure Intensity Percent: 50",
        "    Pressure Intensity Toggle Mode: false",
        "    Left Stick Multiplier: 100",
        "    Right Stick Multiplier: 100",
        "    Left Stick Deadzone: 30",
        "    Right Stick Deadzone: 30",
        "    Left Trigger Threshold: 0",
        "    Right Trigger Threshold: 0",
        "    Left Pad Squircling Factor: 5000",
        "    Right Pad Squircling Factor: 5000",
        "    Color Value R: 0",
        "    Color Value G: 0",
        "    Color Value B: 0",
    ]

    for line in evdev_config_lines:
        f.write(f"{line}\n")


def configure_sdl_controller(
    f: Any, pad: Any, nplayer: int, controller_counts: Any
) -> None:
    """Configure SDL controllers (default fallback)"""
    f.write(f"Player {nplayer} Input:\n")
    f.write("  Handler: SDL\n")
    # workaround controllers with commas in their name - like Nintendo
    ctrlname = pad.name.split(",")[0].strip()
    # rpcs3 appends a unique number per controller name
    if ctrlname in controller_counts:
        controller_counts[ctrlname] += 1
    else:
        controller_counts[ctrlname] = 1
    f.write(f'  Device: "{ctrlname} {controller_counts[ctrlname]}"\n')
    f.write("  Config:\n")
    sdl_config_lines = [
        "    Left Stick Left: LS X-",
        "    Left Stick Down: LS Y-",
        "    Left Stick Right: LS X+",
        "    Left Stick Up: LS Y+",
        "    Right Stick Left: RS X-",
        "    Right Stick Down: RS Y-",
        "    Right Stick Right: RS X+",
        "    Right Stick Up: RS Y+",
        "    Start: Start",
        "    Select: Back",
        "    PS Button: Guide",
        "    Square: X",
        "    Cross: A",
        "    Circle: B",
        "    Triangle: Y",
        "    Left: Left",
        "    Down: Down",
        "    Right: Right",
        "    Up: Up",
        "    R1: RB",
        "    R2: RT",
        "    R3: RS",
        "    L1: LB",
        "    L2: LT",
        "    L3: LS",
        '    IR Nose: ""',
        '    IR Tail: ""',
        '    IR Left: ""',
        '    IR Right: ""',
        '    Tilt Left: ""',
        '    Tilt Right: ""',
        "    Motion Sensor X:",
        "      Axis: X",
        "      Mirrored: false",
        "      Shift: 0",
        "    Motion Sensor Y:",
        "      Axis: Y",
        "      Mirrored: false",
        "      Shift: 0",
        "    Motion Sensor Z:",
        "      Axis: Z",
        "      Mirrored: false",
        "      Shift: 0",
        "    Motion Sensor G:",
        "      Axis: RY",
        "      Mirrored: false",
        "      Shift: 0",
        '    Pressure Intensity Button: ""',
        "    Pressure Intensity Percent: 50",
        "    Pressure Intensity Toggle Mode: false",
        "    Pressure Intensity Deadzone: 0",
        "    Left Stick Multiplier: 100",
        "    Right Stick Multiplier: 100",
        "    Left Stick Deadzone: 8000",
        "    Right Stick Deadzone: 8000",
        "    Left Trigger Threshold: 0",
        "    Right Trigger Threshold: 0",
        "    Left Pad Squircling Factor: 8000",
        "    Right Pad Squircling Factor: 8000",
        "    Color Value R: 0",
        "    Color Value G: 0",
        "    Color Value B: 20",
        "    Blink LED when battery is below 20%: true",
        "    Use LED as a battery indicator: false",
        "    LED battery indicator brightness: 10",
        "    Player LED enabled: true",
        "    Enable Large Vibration Motor: true",
        "    Enable Small Vibration Motor: true",
        "    Switch Vibration Motors: false",
        "    Mouse Movement Mode: Relative",
        "    Mouse Deadzone X Axis: 60",
        "    Mouse Deadzone Y Axis: 60",
        "    Mouse Acceleration X Axis: 200",
        "    Mouse Acceleration Y Axis: 250",
        "    Left Stick Lerp Factor: 100",
        "    Right Stick Lerp Factor: 100",
        "    Analog Button Lerp Factor: 100",
        "    Trigger Lerp Factor: 100",
        "    Device Class Type: 0",
        "    Vendor ID: 1356",
        "    Product ID: 616",
        '  Buddy Device: ""',
    ]

    for line in sdl_config_lines:
        f.write(f"{line}\n")
