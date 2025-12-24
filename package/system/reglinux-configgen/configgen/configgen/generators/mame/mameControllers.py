import xml.etree.ElementTree as ET
from codecs import open
from csv import reader
from os import linesep, path
from typing import Any
from xml.dom import minidom
from xml.dom.minidom import Document, parse

from configgen.utils.logger import get_logger

logger = get_logger(__name__)


def generatePadsConfig(
    cfgPath: str,
    playersControllers: dict,
    sysName: str,
    altButtons: str,
    customCfg: bool,
    specialController: str,
    decorations: str,
    useGuns: bool,
    guns: Any,
    useWheels: bool,
    wheels: dict,
    useMouse: bool,
    multiMouse: bool,
    system: Any,
):
    """
    Generate MAME controller configuration.

    Args:
        cfgPath: Path to the configuration directory
        playersControllers: Dictionary of player controllers
        sysName: Name of the system
        altButtons: Alternative button configuration
        customCfg: Whether using custom configuration
        specialController: Special controller type
        decorations: Decorations setting
        useGuns: Whether to use light guns
        guns: Light gun configuration
        useWheels: Whether to use steering wheels
        wheels: Wheel configuration
        useMouse: Whether to use mouse
        multiMouse: Whether to use multiple mice
        system: System configuration
    """
    # Load control mappings
    control_dict = _load_control_mappings()

    # Create main configuration
    config, config_file, overwrite_mame = _initialize_main_config(cfgPath, customCfg)

    # Get base mappings
    mappings = _get_base_mappings(control_dict)
    gunmappings = _get_gun_mappings(control_dict, useGuns)
    mousemappings = _get_mouse_mappings(control_dict, useMouse)
    if altButtons in control_dict:
        _update_alt_mappings(mappings, control_dict, altButtons)

    # Initialize XML structure
    xml_mameconfig = getRoot(config, "mameconfig")
    xml_mameconfig.setAttribute("version", "10")
    xml_system = getSection(config, xml_mameconfig, "system")
    xml_system.setAttribute("name", "default")

    # Configure crosshairs
    _configure_crosshairs(config, xml_system, system)

    # Initialize input section
    removeSection(config, xml_system, "input")
    xml_input = config.createElement("input")
    xml_system.appendChild(xml_input)

    # Handle special controllers
    config_alt, configFile_alt, xml_input_alt, overwriteSystem = (
        _handle_special_controllers(
            sysName, specialController, cfgPath, customCfg, decorations
        )
    )

    # Process players' controllers
    special_control_list = _get_special_control_list()
    use_controls = _determine_control_set(sysName, specialController)
    _process_players_controllers(
        config,
        xml_input,
        playersControllers,
        mappings,
        useWheels,
        wheels,
        gunmappings,
        mousemappings,
        multiMouse,
        system,
        altButtons,
        special_control_list,
        sysName,
        config_alt,
        xml_input_alt,
        use_controls,
    )

    # Configure additional guns if needed
    if useGuns and len(guns) > len(playersControllers):
        _configure_additional_guns(
            config, xml_input, playersControllers, guns, gunmappings, system
        )

    # Save main config file
    if overwrite_mame:
        logger.debug(f"Saving {config_file}")
        _save_config_file(config, config_file)

    # Save alternative config if needed
    if (
        sysName in special_control_list
        and overwriteSystem is not None
        and overwriteSystem
        and configFile_alt is not None
        and config_alt is not None
    ):
        logger.debug(f"Saving {configFile_alt}")
        mameXml_alt = open(configFile_alt, "w", "utf-8")
        dom_string_alt = linesep.join(
            [s for s in config_alt.toprettyxml().splitlines() if s.strip()]
        )  # remove ugly empty lines while minicom adds them...
        mameXml_alt.write(dom_string_alt)


def _load_control_mappings() -> dict[str, dict[str, str]]:
    """Load control mappings from CSV file."""
    control_file = "/usr/share/reglinux/configgen/data/mame/mameControls.csv"
    open_file = open(control_file, "r")
    control_dict = {}
    with open_file:
        control_list = reader(open_file)
        for row in control_list:
            if row[0] not in control_dict:
                control_dict[row[0]] = {}
            control_dict[row[0]][row[1]] = row[2]
    return control_dict


def _initialize_main_config(
    cfg_path: str, custom_cfg: bool
) -> tuple[Document, str, bool]:
    """Initialize main configuration document and determine overwrite status."""
    config = Document()
    config_file = cfg_path + "default.cfg"

    if path.exists(config_file):
        try:
            config = parse(config_file)
        except (ET.ParseError, FileNotFoundError):
            pass  # reinit the file

    overwrite_mame = not (path.exists(config_file) and custom_cfg)
    return config, config_file, overwrite_mame


def _get_base_mappings(control_dict: dict[str, dict[str, str]]) -> dict[str, str]:
    """Get base control mappings."""
    mappings = {}
    for control_def in control_dict["default"].keys():
        mappings[control_def] = control_dict["default"][control_def]
    return mappings


def _get_gun_mappings(
    control_dict: dict[str, dict[str, str]], use_guns: bool
) -> dict[str, str]:
    """Get gun button mappings if guns are enabled."""
    gunmappings = {}
    if use_guns:
        for control_def in control_dict["gunbuttons"].keys():
            gunmappings[control_def] = control_dict["gunbuttons"][control_def]
    return gunmappings


def _get_mouse_mappings(
    control_dict: dict[str, dict[str, str]], use_mouse: bool
) -> dict[str, str]:
    """Get mouse button mappings if mouse is enabled."""
    mousemappings = {}
    if use_mouse:
        for control_def in control_dict["mousebuttons"].keys():
            mousemappings[control_def] = control_dict["mousebuttons"][control_def]
    return mousemappings


def _update_alt_mappings(
    mappings: dict[str, str], control_dict: dict[str, dict[str, str]], alt_buttons: str
):
    """Update mappings with alternative button configuration."""
    for control_def in control_dict[alt_buttons].keys():
        mappings.update({control_def: control_dict[alt_buttons][control_def]})


def _configure_crosshairs(config: Document, xml_system: Any, system: Any):
    """Configure crosshairs settings."""
    removeSection(config, xml_system, "crosshairs")
    xml_crosshairs = config.createElement("crosshairs")
    for p in range(0, 4):
        xml_crosshair = config.createElement("crosshair")
        xml_crosshair.setAttribute("player", str(p))
        if system.isOptSet("mame_crosshair") and system.config["mame_crosshair"] == "1":
            xml_crosshair.setAttribute("mode", "1")
        else:
            xml_crosshair.setAttribute("mode", "0")
        xml_crosshairs.appendChild(xml_crosshair)
    xml_system.appendChild(xml_crosshairs)


def _get_special_control_list() -> list[str]:
    """Get list of systems with special controller configurations."""
    return [
        "cdimono1",
        "apfm1000",
        "astrocde",
        "adam",
        "arcadia",
        "gamecom",
        "tutor",
        "crvision",
        "bbcb",
        "bbcm",
        "bbcm512",
        "bbcmc",
        "xegs",
        "socrates",
        "pdp1",
        "vc4000",
        "fmtmarty",
        "gp32",
        "apple2p",
        "apple2e",
        "apple2ee",
    ]


def _determine_control_set(sys_name: str, special_controller: str) -> str:
    """Determine which control set to use based on system and special controller."""
    if sys_name in ["bbcb", "bbcm", "bbcm512", "bbcmc"]:
        if special_controller == "none":
            use_controls = "bbc"
        else:
            use_controls = f"bbc-{special_controller}"
    elif sys_name in ["apple2p", "apple2e", "apple2ee"]:
        if special_controller == "none":
            use_controls = "apple2"
        else:
            use_controls = f"apple2-{special_controller}"
    else:
        use_controls = sys_name
    logger.debug(f"Using {use_controls} for controller config.")
    return use_controls


def _load_mess_control_mappings() -> dict[str, Any]:
    """Load MESS control mappings from CSV file."""
    mess_control_file = "/usr/share/reglinux/configgen/data/mame/messControls.csv"
    mess_control_dict = {}
    with open(mess_control_file, "r") as open_mess_file:
        control_list = reader(open_mess_file, delimiter=";")
        for row in control_list:
            if row[0] not in mess_control_dict:
                mess_control_dict[row[0]] = {}
            mess_control_dict[row[0]][row[1]] = {}
            current_entry = mess_control_dict[row[0]][row[1]]
            current_entry["type"] = row[2]
            current_entry["player"] = int(row[3])
            current_entry["tag"] = row[4]
            current_entry["key"] = row[5]
            if current_entry["type"] in ["special", "main"]:
                current_entry["mapping"] = row[6]
                current_entry["useMapping"] = row[7]
                current_entry["reversed"] = row[8]
                current_entry["mask"] = row[9]
                current_entry["default"] = row[10]
            elif current_entry["type"] == "analog":
                current_entry["incMapping"] = row[6]
                current_entry["decMapping"] = row[7]
                current_entry["useMapping1"] = row[8]
                current_entry["useMapping2"] = row[9]
                current_entry["reversed"] = row[10]
                current_entry["mask"] = row[11]
                current_entry["default"] = row[12]
                current_entry["delta"] = row[13]
                current_entry["axis"] = row[14]
            if current_entry["type"] == "combo":
                current_entry["kbMapping"] = row[6]
                current_entry["mapping"] = row[7]
                current_entry["useMapping"] = row[8]
                current_entry["reversed"] = row[9]
                current_entry["mask"] = row[10]
                current_entry["default"] = row[11]
    return mess_control_dict


def _handle_special_controllers(
    sys_name: str,
    special_controller: str,
    cfg_path: str,
    custom_cfg: bool,
    decorations: str,
) -> tuple[minidom.Document | None, str | None, Any, bool | None]:
    """Handle special controller configurations."""
    special_control_list = _get_special_control_list()

    if sys_name not in special_control_list:
        return None, None, None, None

    config_alt = minidom.Document()
    config_file_alt = cfg_path + sys_name + ".cfg"

    if (
        path.exists(config_file_alt)
        and cfg_path == f"/userdata/system/configs/mame/{sys_name}/"
    ) or path.exists(config_file_alt):
        try:
            config_alt = minidom.parse(config_file_alt)
        except Exception:
            pass  # reinit the file

    per_game_cfg = cfg_path != f"/userdata/system/configs/mame/{sys_name}/"
    overwrite_system = not (
        path.exists(config_file_alt) and (custom_cfg or per_game_cfg)
    )

    xml_mameconfig_alt = getRoot(config_alt, "mameconfig")
    xml_mameconfig_alt.setAttribute("version", "10")
    xml_system_alt = getSection(config_alt, xml_mameconfig_alt, "system")
    xml_system_alt.setAttribute("name", sys_name)

    removeSection(config_alt, xml_system_alt, "input")
    xml_input_alt = config_alt.createElement("input")
    xml_system_alt.appendChild(xml_input_alt)

    use_controls = _determine_control_set(sys_name, special_controller)

    # Configure special display settings
    if use_controls == "cdimono1":
        _configure_lcd_display(config_alt, xml_system_alt, decorations)

    # Enable keyboard for BBC systems
    if use_controls == "bbc":
        _enable_bbc_keyboard(config_alt, xml_input_alt)

    return config_alt, config_file_alt, xml_input_alt, overwrite_system


def _configure_lcd_display(
    config_alt: minidom.Document, xml_system_alt: Any, decorations: str
):
    """Configure LCD display settings for CD-i."""
    removeSection(config_alt, xml_system_alt, "video")
    xml_video_alt = config_alt.createElement("video")
    xml_system_alt.appendChild(xml_video_alt)

    xml_screencfg_alt = config_alt.createElement("target")
    xml_screencfg_alt.setAttribute("index", "0")
    if decorations == "none":
        xml_screencfg_alt.setAttribute("view", "Main Screen Standard (4:3)")
    else:
        xml_screencfg_alt.setAttribute("view", "Upright_Artwork")
    xml_video_alt.appendChild(xml_screencfg_alt)


def _enable_bbc_keyboard(config_alt: minidom.Document, xml_input_alt: Any):
    """Enable keyboard for BBC systems."""
    xml_kbenable_alt = config_alt.createElement("keyboard")
    xml_kbenable_alt.setAttribute("tag", ":")
    xml_kbenable_alt.setAttribute("enabled", "1")
    xml_input_alt.appendChild(xml_kbenable_alt)


def _process_players_controllers(
    config: Document,
    xml_input: Any,
    players_controllers: dict,
    mappings: dict[str, str],
    use_wheels: bool,
    wheels: dict,
    gunmappings: dict[str, str],
    mousemappings: dict[str, str],
    multi_mouse: bool,
    system: Any,
    alt_buttons: str,
    special_control_list: list[str],
    sys_name: str,
    config_alt: minidom.Document | None,
    xml_input_alt: Any,
    use_controls: str,
):
    """Process configuration for each player's controller."""
    for nplayer, pad in enumerate(sorted(players_controllers.items()), start=1):
        _, pad = pad  # Extract the pad from the tuple

        # Get mappings for this player
        mappings_use = mappings.copy()
        if not hasStick(pad):
            mappings_use["JOYSTICK_UP"] = "up"
            mappings_use["JOYSTICK_DOWN"] = "down"
            mappings_use["JOYSTICK_LEFT"] = "left"
            mappings_use["JOYSTICK_RIGHT"] = "right"

        # Handle wheel mappings
        is_wheel = _check_wheel_mapping(pad, nplayer, use_wheels, wheels, mappings_use)

        # Add common player ports
        addCommonPlayerPorts(config, xml_input, nplayer)

        # Get pedal key for this player
        pedalkey = _get_pedal_key(nplayer, system)

        # Process each mapping
        _process_player_mappings(
            config,
            xml_input,
            pad,
            nplayer,
            mappings_use,
            is_wheel,
            gunmappings,
            mousemappings,
            multi_mouse,
            alt_buttons,
            pedalkey,
        )

        # Add UI mappings for player 1
        if nplayer == 1:
            _add_ui_mappings(config, xml_input, pad, mappings_use, pedalkey)

        # Handle special controller mappings
        if (
            sys_name in special_control_list
            and config_alt is not None
            and xml_input_alt is not None
        ):
            _process_special_controller_mappings(
                pad,
                nplayer,
                config_alt,
                xml_input_alt,
                use_controls,
                mappings_use,
                special_control_list,
                sys_name,
                pedalkey,
            )


def _check_wheel_mapping(
    pad: Any, nplayer: int, use_wheels: bool, wheels: dict, mappings_use: dict[str, str]
) -> bool:
    """
    Check if the pad has a wheel and update mappings accordingly.

    Args:
        pad: Controller pad object
        nplayer: Player number
        use_wheels: Whether steering wheels are in use
        wheels: Wheel configuration dictionary
        mappings_use: The current mappings dictionary to update

    Returns:
        True if the pad is a wheel, False otherwise
    """
    is_wheel = False
    if use_wheels:
        for w in wheels:
            if wheels[w]["joystick_index"] == pad.index:
                is_wheel = True
                logger.debug(f"player {nplayer} has a wheel")
                break
        if is_wheel:
            # Remove certain mappings for wheel
            mappings_to_remove = []
            for x in list(mappings_use.keys()):
                if (
                    mappings_use[x] == "l2"
                    or mappings_use[x] == "r2"
                    or mappings_use[x] == "joystick1left"
                ):
                    mappings_to_remove.append(x)
            for x in mappings_to_remove:
                del mappings_use[x]

            # Add wheel-specific mappings
            mappings_use[f"PEDAL{pad.index + 1}"] = "r2"
            mappings_use[f"PEDAL2{pad.index + 1}"] = "l2"
            mappings_use[f"PADDLE{pad.index + 1}"] = "joystick1left"
    return is_wheel


def _get_pedal_key(nplayer: int, system: Any) -> str | None:
    """Get the appropriate pedal key for the player."""
    pedals_keys = {1: "c", 2: "v", 3: "b", 4: "n"}
    pedalkey = None
    pedal_cname = f"controllers.pedals{nplayer}"
    if pedal_cname in system.config:
        pedalkey = system.config[pedal_cname]
    else:
        if nplayer in pedals_keys:
            pedalkey = pedals_keys[nplayer]
    return pedalkey


def _process_player_mappings(
    config: Document,
    xml_input: Any,
    pad: Any,
    nplayer: int,
    mappings_use: dict[str, str],
    is_wheel: bool,
    gunmappings: dict[str, str],
    mousemappings: dict[str, str],
    multi_mouse: bool,
    alt_buttons: str,
    pedalkey: str | None,
):
    """Process mappings for a specific player."""
    for mapping in mappings_use:
        if mappings_use[mapping] in pad.inputs:
            if mapping in ["START", "COIN"]:
                xml_input.appendChild(
                    generateSpecialPortElementPlayer(
                        pad,
                        config,
                        "standard",
                        nplayer,
                        pad.index,
                        mapping,
                        mappings_use[mapping],
                        pad.inputs[mappings_use[mapping]],
                        False,
                        "",
                        "",
                        gunmappings,
                        mousemappings,
                        multi_mouse,
                        pedalkey,
                    )
                )
            else:
                xml_input.appendChild(
                    generatePortElement(
                        pad,
                        config,
                        nplayer,
                        pad.index,
                        mapping,
                        mappings_use[mapping],
                        pad.inputs[mappings_use[mapping]],
                        False,
                        alt_buttons,
                        gunmappings,
                        is_wheel,
                        mousemappings,
                        multi_mouse,
                        pedalkey,
                    )
                )
        else:
            rmapping = reverseMapping(mappings_use[mapping])
            if rmapping in pad.inputs:
                xml_input.appendChild(
                    generatePortElement(
                        pad,
                        config,
                        nplayer,
                        pad.index,
                        mapping,
                        mappings_use[mapping],
                        pad.inputs[rmapping],
                        True,
                        alt_buttons,
                        gunmappings,
                        is_wheel,
                        mousemappings,
                        multi_mouse,
                        pedalkey,
                    )
                )


def _add_ui_mappings(
    config: Document,
    xml_input: Any,
    pad: Any,
    mappings_use: dict[str, str],
    pedalkey: str | None,
):
    """Add UI mappings for player 1."""
    xml_input.appendChild(
        generateComboPortElement(
            pad,
            config,
            "standard",
            pad.index,
            "UI_DOWN",
            "DOWN",
            mappings_use["JOYSTICK_DOWN"],
            pad.inputs[mappings_use["JOYSTICK_UP"]],
            False,
            "",
            "",
        )
    )  # Down
    xml_input.appendChild(
        generateComboPortElement(
            pad,
            config,
            "standard",
            pad.index,
            "UI_LEFT",
            "LEFT",
            mappings_use["JOYSTICK_LEFT"],
            pad.inputs[mappings_use["JOYSTICK_LEFT"]],
            False,
            "",
            "",
        )
    )  # Left
    xml_input.appendChild(
        generateComboPortElement(
            pad,
            config,
            "standard",
            pad.index,
            "UI_UP",
            "UP",
            mappings_use["JOYSTICK_UP"],
            pad.inputs[mappings_use["JOYSTICK_UP"]],
            False,
            "",
            "",
        )
    )  # Up
    xml_input.appendChild(
        generateComboPortElement(
            pad,
            config,
            "standard",
            pad.index,
            "UI_RIGHT",
            "RIGHT",
            mappings_use["JOYSTICK_RIGHT"],
            pad.inputs[mappings_use["JOYSTICK_LEFT"]],
            False,
            "",
            "",
        )
    )  # Right
    xml_input.appendChild(
        generateComboPortElement(
            pad,
            config,
            "standard",
            pad.index,
            "UI_SELECT",
            "ENTER",
            "b",
            pad.inputs["b"],
            False,
            "",
            "",
        )
    )  # Select


def _process_special_controller_mappings(
    pad: Any,
    nplayer: int,
    config_alt: minidom.Document,
    xml_input_alt: Any,
    use_controls: str,
    mappings_use: dict[str, str],
    special_control_list: list[str],
    sys_name: str,
    pedalkey: str | None,
):
    """Process special controller mappings for specific systems."""
    mess_control_dict = _load_mess_control_mappings()
    if use_controls in mess_control_dict:
        for control_def in mess_control_dict[use_controls].keys():
            this_control = mess_control_dict[use_controls][control_def]
            if nplayer == this_control["player"]:
                if this_control["type"] == "special" or this_control["type"] == "main":
                    xml_input_alt.appendChild(
                        generateSpecialPortElement(
                            pad,
                            config_alt,
                            this_control["tag"],
                            nplayer,
                            pad.index,
                            this_control["key"],
                            this_control["mapping"],
                            pad.inputs[mappings_use[this_control["useMapping"]]],
                            this_control["reversed"],
                            this_control["mask"],
                            this_control["default"],
                            pedalkey,
                        )
                    )
                elif this_control["type"] == "analog":
                    xml_input_alt.appendChild(
                        generateAnalogPortElement(
                            pad,
                            config_alt,
                            this_control["tag"],
                            nplayer,
                            pad.index,
                            this_control["key"],
                            mappings_use[this_control["incMapping"]],
                            mappings_use[this_control["decMapping"]],
                            pad.inputs[mappings_use[this_control["useMapping1"]]],
                            pad.inputs[mappings_use[this_control["useMapping2"]]],
                            this_control["reversed"],
                            this_control["mask"],
                            this_control["default"],
                            this_control["delta"],
                            this_control["axis"],
                        )
                    )
                elif this_control["type"] == "combo":
                    xml_input_alt.appendChild(
                        generateComboPortElement(
                            pad,
                            config_alt,
                            this_control["tag"],
                            pad.index,
                            this_control["key"],
                            this_control["kbMapping"],
                            this_control["mapping"],
                            pad.inputs[mappings_use[this_control["useMapping"]]],
                            this_control["reversed"],
                            this_control["mask"],
                            this_control["default"],
                        )
                    )


def _configure_additional_guns(
    config: Document,
    xml_input: Any,
    players_controllers: dict,
    guns: Any,
    gunmappings: dict[str, str],
    system: Any,
):
    """Configure additional guns beyond the number of controllers."""
    for gunnum in range(len(players_controllers) + 1, len(guns) + 1):
        pedalkey = _get_pedal_key(gunnum, system)
        addCommonPlayerPorts(config, xml_input, gunnum)
        for mapping in gunmappings:
            gun_port = generateGunPortElement(
                config, gunnum, mapping, gunmappings, pedalkey
            )
            if gun_port is not None:
                xml_input.appendChild(gun_port)


def _save_config_file(config: Document, config_file: str):
    """Save the main configuration file."""
    with open(config_file, "w", "utf-8") as mameXml:
        dom_string = linesep.join(
            [s for s in config.toprettyxml().splitlines() if s.strip()]
        )  # remove ugly empty lines while minicom adds them...
        mameXml.write(dom_string)


def reverseMapping(key: str) -> str | None:
    """
    Get the reverse mapping for a key.

    Args:
        key: The key to reverse

    Returns:
        The reversed key or None if no reverse mapping exists
    """
    if key == "joystick1down":
        return "joystick1up"
    if key == "joystick1right":
        return "joystick1left"
    if key == "joystick2down":
        return "joystick2up"
    if key == "joystick2right":
        return "joystick2left"
    return None


def generatePortElement(
    pad: Any,
    config: Document,
    nplayer: int,
    padindex: int,
    mapping: str,
    key: str,
    input: Any,
    reversed: bool,
    altButtons: str,
    gunmappings: dict[str, str],
    isWheel: bool,
    mousemappings: dict[str, str],
    multiMouse: bool,
    pedalkey: str | None,
) -> Any:
    """
    Generate a port element for the MAME configuration.

    Args:
        pad: Controller pad object
        config: XML configuration document
        nplayer: Player number
        padindex: Index of the pad
        mapping: Input mapping name
        key: Input key
        input: Input object
        reversed: Whether the input is reversed
        altButtons: Alternative buttons configuration
        gunmappings: Gun mappings
        isWheel: Whether this is a wheel controller
        mousemappings: Mouse mappings
        multiMouse: Whether multiple mice are used
        pedalkey: Pedal key for gun controls

    Returns:
        The generated XML port element
    """
    # Generic input
    xml_port = config.createElement("port")
    xml_port.setAttribute("type", f"P{nplayer}_{mapping}")
    xml_newseq = config.createElement("newseq")
    xml_newseq.setAttribute("type", "standard")
    xml_port.appendChild(xml_newseq)
    keyval = input2definition(
        pad, key, input, padindex, reversed, altButtons, False, isWheel
    )
    if mapping in gunmappings:
        keyval = keyval + f" OR GUNCODE_{nplayer}_{gunmappings[mapping]}"
        if gunmappings[mapping] == "BUTTON2" and pedalkey is not None:
            keyval += " OR KEYCODE_" + pedalkey.upper()
    if mapping in mousemappings:
        if multiMouse:
            keyval = keyval + f" OR MOUSECODE_{nplayer}_{mousemappings[mapping]}"
        else:
            keyval = keyval + f" OR MOUSECODE_1_{mousemappings[mapping]}"
    value = config.createTextNode(keyval)
    xml_newseq.appendChild(value)
    return xml_port


def generateGunPortElement(
    config: Document,
    nplayer: int,
    mapping: str,
    gunmappings: dict[str, str],
    pedalkey: str | None,
) -> Any | None:
    """
    Generate a port element specifically for gun controls.

    Args:
        config: XML configuration document
        nplayer: Player number
        mapping: Input mapping name
        gunmappings: Gun mappings
        pedalkey: Pedal key for gun controls

    Returns:
        The generated XML port element or None if no mapping exists
    """
    # Generic input
    xml_port = config.createElement("port")
    if mapping in ["START", "COIN"]:
        xml_port.setAttribute("type", mapping + str(nplayer))
    else:
        xml_port.setAttribute("type", f"P{nplayer}_{mapping}")
    xml_newseq = config.createElement("newseq")
    xml_newseq.setAttribute("type", "standard")
    xml_port.appendChild(xml_newseq)
    keyval = None
    if mapping in gunmappings:
        keyval = f"GUNCODE_{nplayer}_{gunmappings[mapping]}"
        if gunmappings[mapping] == "BUTTON2" and pedalkey is not None:
            keyval += " OR KEYCODE_" + pedalkey.upper()
    if keyval is None:
        return None
    value = config.createTextNode(keyval)
    xml_newseq.appendChild(value)
    return xml_port


def generateSpecialPortElementPlayer(
    pad: Any,
    config: Document,
    tag: str,
    nplayer: int,
    padindex: int,
    mapping: str,
    key: str,
    input: Any,
    reversed: bool,
    mask: str,
    default: str,
    gunmappings: dict[str, str],
    mousemappings: dict[str, str],
    multiMouse: bool,
    pedalkey: str | None,
) -> Any:
    """
    Generate a special port element for player-specific controls.

    Args:
        pad: Controller pad object
        config: XML configuration document
        tag: Tag for the port
        nplayer: Player number
        padindex: Index of the pad
        mapping: Input mapping name
        key: Input key
        input: Input object
        reversed: Whether the input is reversed
        mask: Mask value
        default: Default value
        gunmappings: Gun mappings
        mousemappings: Mouse mappings
        multiMouse: Whether multiple mice are used
        pedalkey: Pedal key for gun controls

    Returns:
        The generated XML port element
    """
    # Special button input (ie mouse button to gamepad)
    xml_port = config.createElement("port")
    xml_port.setAttribute("tag", tag)
    xml_port.setAttribute("type", mapping + str(nplayer))
    xml_port.setAttribute("mask", mask)
    xml_port.setAttribute("defvalue", default)
    xml_newseq = config.createElement("newseq")
    xml_newseq.setAttribute("type", "standard")
    xml_port.appendChild(xml_newseq)
    keyval = input2definition(pad, key, input, padindex, reversed, "0")
    if mapping in gunmappings:
        keyval = keyval + f" OR GUNCODE_{nplayer}_{gunmappings[mapping]}"
        if gunmappings[mapping] == "BUTTON2" and pedalkey is not None:
            keyval += " OR KEYCODE_" + pedalkey.upper()
    if mapping in mousemappings:
        if multiMouse:
            keyval = keyval + f" OR MOUSECODE_{nplayer}_{mousemappings[mapping]}"
        else:
            keyval = keyval + f" OR MOUSECODE_1_{mousemappings[mapping]}"
    value = config.createTextNode(keyval)
    xml_newseq.appendChild(value)
    return xml_port


def generateSpecialPortElement(
    pad: Any,
    config: Document,
    tag: str,
    nplayer: int,
    padindex: int,
    mapping: str,
    key: str,
    input: Any,
    reversed: bool,
    mask: str,
    default: str,
    pedalkey: str | None,
) -> Any:
    """
    Generate a special port element.

    Args:
        pad: Controller pad object
        config: XML configuration document
        tag: Tag for the port
        nplayer: Player number
        padindex: Index of the pad
        mapping: Input mapping name
        key: Input key
        input: Input object
        reversed: Whether the input is reversed
        mask: Mask value
        default: Default value
        pedalkey: Pedal key for gun controls

    Returns:
        The generated XML port element
    """
    # Special button input (ie mouse button to gamepad)
    xml_port = config.createElement("port")
    xml_port.setAttribute("tag", tag)
    xml_port.setAttribute("type", mapping)
    xml_port.setAttribute("mask", mask)
    xml_port.setAttribute("defvalue", default)
    xml_newseq = config.createElement("newseq")
    xml_newseq.setAttribute("type", "standard")
    xml_port.appendChild(xml_newseq)
    value = config.createTextNode(
        input2definition(pad, key, input, padindex, reversed, "0")
    )
    xml_newseq.appendChild(value)
    return xml_port


def generateComboPortElement(
    pad: Any,
    config: Document,
    tag: str,
    padindex: int,
    mapping: str,
    kbkey: str,
    key: str,
    input: Any,
    reversed: bool,
    mask: str,
    default: str,
) -> Any:
    """
    Generate a combo port element.

    Args:
        pad: Controller pad object
        config: XML configuration document
        tag: Tag for the port
        padindex: Index of the pad
        mapping: Input mapping name
        kbkey: Keyboard key
        key: Input key
        input: Input object
        reversed: Whether the input is reversed
        mask: Mask value
        default: Default value

    Returns:
        The generated XML port element
    """
    # Maps a keycode + button - for important keyboard keys when available
    xml_port = config.createElement("port")
    xml_port.setAttribute("tag", tag)
    xml_port.setAttribute("type", mapping)
    xml_port.setAttribute("mask", mask)
    xml_port.setAttribute("defvalue", default)
    xml_newseq = config.createElement("newseq")
    xml_newseq.setAttribute("type", "standard")
    xml_port.appendChild(xml_newseq)
    value = config.createTextNode(
        f"KEYCODE_{kbkey} OR "
        + input2definition(pad, key, input, padindex, reversed, "0")
    )
    xml_newseq.appendChild(value)
    return xml_port


def generateAnalogPortElement(
    pad: Any,
    config: Document,
    tag: str,
    nplayer: int,
    padindex: int,
    mapping: str,
    inckey: str,
    deckey: str,
    mappedinput: Any,
    mappedinput2: Any,
    reversed: bool,
    mask: str,
    default: str,
    delta: str,
    axis: str = "",
) -> Any:
    """
    Generate an analog port element.

    Args:
        pad: Controller pad object
        config: XML configuration document
        tag: Tag for the port
        nplayer: Player number
        padindex: Index of the pad
        mapping: Input mapping name
        inckey: Key for increment action
        deckey: Key for decrement action
        mappedinput: First mapped input
        mappedinput2: Second mapped input
        reversed: Whether the input is reversed
        mask: Mask value
        default: Default value
        delta: Delta value for analog controls
        axis: Axis for joystick controls (optional)

    Returns:
        The generated XML port element
    """
    # Mapping analog to digital (mouse, etc)
    xml_port = config.createElement("port")
    xml_port.setAttribute("tag", tag)
    xml_port.setAttribute("type", mapping)
    xml_port.setAttribute("mask", mask)
    xml_port.setAttribute("defvalue", default)
    xml_port.setAttribute("keydelta", delta)
    xml_newseq_inc = config.createElement("newseq")
    xml_newseq_inc.setAttribute("type", "increment")
    xml_port.appendChild(xml_newseq_inc)
    incvalue = config.createTextNode(
        input2definition(pad, inckey, mappedinput, padindex, reversed, "0", True)
    )
    xml_newseq_inc.appendChild(incvalue)
    xml_newseq_dec = config.createElement("newseq")
    xml_port.appendChild(xml_newseq_dec)
    xml_newseq_dec.setAttribute("type", "decrement")
    decvalue = config.createTextNode(
        input2definition(pad, deckey, mappedinput2, padindex, reversed, "0", True)
    )
    xml_newseq_dec.appendChild(decvalue)
    xml_newseq_std = config.createElement("newseq")
    xml_port.appendChild(xml_newseq_std)
    xml_newseq_std.setAttribute("type", "standard")
    if axis == "":
        stdvalue = config.createTextNode("NONE")
    else:
        stdvalue = config.createTextNode(f"JOYCODE_{padindex}_{axis}")
    xml_newseq_std.appendChild(stdvalue)
    return xml_port


def input2definition(
    pad: Any,
    key: str,
    input: Any,
    joycode: int,
    reversed: bool,
    altButtons: str,
    ignoreAxis: bool = False,
    isWheel: bool = False,
) -> str:
    """
    Convert input to MAME definition string.

    Args:
        pad: Controller pad object
        key: Input key
        input: Input object
        joycode: Joystick code
        reversed: Whether the input is reversed
        altButtons: Alternative buttons configuration
        ignoreAxis: Whether to ignore axis inputs
        isWheel: Whether this is a wheel controller

    Returns:
        MAME input definition string
    """
    mame_axis_mapping_names = {
        0: "XAXIS",
        1: "YAXIS",
        2: "ZAXIS",
        3: "RXAXIS",
        4: "RYAXIS",
        5: "RZAXIS",
    }

    if isWheel:
        if key == "joystick1left" or key == "l2" or key == "r2":
            suffix = ""
            if key == "r2":
                suffix = "_NEG"
            if key == "l2":
                suffix = "_NEG"
            if int(input.id) in mame_axis_mapping_names:
                idname = mame_axis_mapping_names[int(input.id)]
                return f"JOYCODE_{joycode}_{idname}{suffix}"

    if input.type == "button":
        return f"JOYCODE_{joycode}_BUTTON{int(input.id) + 1}"
    elif input.type == "hat":
        if input.value == "1":
            return f"JOYCODE_{joycode}_HAT1UP"
        elif input.value == "2":
            return f"JOYCODE_{joycode}_HAT1RIGHT"
        elif input.value == "4":
            return f"JOYCODE_{joycode}_HAT1DOWN"
        elif input.value == "8":
            return f"JOYCODE_{joycode}_HAT1LEFT"
    elif input.type == "axis":
        # Determine alternate button for D-Pad and right stick as buttons
        dpad_inputs = {}
        for direction in ["up", "down", "left", "right"]:
            if pad.inputs[direction].type == "button":
                dpad_inputs[direction] = (
                    f"JOYCODE_{joycode}_BUTTON{int(pad.inputs[direction].id) + 1}"
                )
            elif pad.inputs[direction].type == "hat":
                if pad.inputs[direction].value == "1":
                    dpad_inputs[direction] = f"JOYCODE_{joycode}_HAT1UP"
                if pad.inputs[direction].value == "2":
                    dpad_inputs[direction] = f"JOYCODE_{joycode}_HAT1RIGHT"
                if pad.inputs[direction].value == "4":
                    dpad_inputs[direction] = f"JOYCODE_{joycode}_HAT1DOWN"
                if pad.inputs[direction].value == "8":
                    dpad_inputs[direction] = f"JOYCODE_{joycode}_HAT1LEFT"
            else:
                dpad_inputs[direction] = ""
        button_directions = {}
        # workarounds for issue #6892
        # Modified because right stick to buttons was not working after the workaround
        # Creates a blank, only modifies if the button exists in the pad.
        # Button assigment modified - blank "OR" gets removed by MAME if the button is undefined.
        for direction in ["a", "b", "x", "y"]:
            button_directions[direction] = ""
            if direction in pad.inputs.keys():
                if pad.inputs[direction].type == "button":
                    button_directions[direction] = (
                        f"JOYCODE_{joycode}_BUTTON{int(pad.inputs[direction].id) + 1}"
                    )

        if (
            ignoreAxis
            and dpad_inputs["up"] != ""
            and dpad_inputs["down"] != ""
            and dpad_inputs["left"] != ""
            and dpad_inputs["right"] != ""
        ):
            if key == "joystick1up" or key == "up":
                return dpad_inputs["up"]
            if key == "joystick1down" or key == "down":
                return dpad_inputs["down"]
            if key == "joystick1left" or key == "left":
                return dpad_inputs["left"]
            if key == "joystick1right" or key == "right":
                return dpad_inputs["right"]
        if altButtons == "qbert":  # Q*Bert Joystick
            if key == "joystick1up" or key == "up":
                return f"JOYCODE_{joycode}_YAXIS_UP_SWITCH JOYCODE_{joycode}_XAXIS_RIGHT_SWITCH OR {dpad_inputs['up']} {dpad_inputs['right']}"
            if key == "joystick1down" or key == "down":
                return f"JOYCODE_{joycode}_YAXIS_DOWN_SWITCH JOYCODE_{joycode}_XAXIS_LEFT_SWITCH OR {dpad_inputs['down']} {dpad_inputs['left']}"
            if key == "joystick1left" or key == "left":
                return f"JOYCODE_{joycode}_XAXIS_LEFT_SWITCH JOYCODE_{joycode}_YAXIS_UP_SWITCH OR {dpad_inputs['left']} {dpad_inputs['up']}"
            if key == "joystick1right" or key == "right":
                return f"JOYCODE_{joycode}_XAXIS_RIGHT_SWITCH JOYCODE_{joycode}_YAXIS_DOWN_SWITCH OR {dpad_inputs['right']} {dpad_inputs['down']}"
        else:
            if key == "joystick1up" or key == "up":
                return f"JOYCODE_{joycode}_YAXIS_UP_SWITCH OR {dpad_inputs['up']}"
            if key == "joystick1down" or key == "down":
                return f"JOYCODE_{joycode}_YAXIS_DOWN_SWITCH OR {dpad_inputs['down']}"
            if key == "joystick1left" or key == "left":
                return f"JOYCODE_{joycode}_XAXIS_LEFT_SWITCH OR {dpad_inputs['left']}"
            if key == "joystick1right" or key == "right":
                return f"JOYCODE_{joycode}_XAXIS_RIGHT_SWITCH OR {dpad_inputs['right']}"
        # Fix for the workaround
        for direction in pad.inputs:
            if key == "joystick2up":
                return (
                    f"JOYCODE_{joycode}_RYAXIS_NEG_SWITCH OR {button_directions['x']}"
                )
            if key == "joystick2down":
                return (
                    f"JOYCODE_{joycode}_RYAXIS_POS_SWITCH OR {button_directions['b']}"
                )
            if key == "joystick2left":
                return (
                    f"JOYCODE_{joycode}_RXAXIS_NEG_SWITCH OR {button_directions['y']}"
                )
            if key == "joystick2right":
                return (
                    f"JOYCODE_{joycode}_RXAXIS_POS_SWITCH OR {button_directions['a']}"
                )
            if int(input.id) in mame_axis_mapping_names:
                idname = mame_axis_mapping_names[int(input.id)]
                return f"JOYCODE_{joycode}_{idname}_POS_SWITCH"

    return "unknown"


def _safe_int_conversion(value: Any, default: int = 0) -> int:
    """
    Safely convert a value to an integer.

    Args:
        value: The value to convert
        default: Default value if conversion fails

    Returns:
        The converted integer or the default value
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def hasStick(pad: Any) -> bool:
    """
    Check if the pad has a joystick stick.

    Args:
        pad: Controller pad object

    Returns:
        True if the pad has a joystick stick, False otherwise
    """
    return "joystick1up" in pad.inputs


def getRoot(config: Document, name: str) -> Any:
    """
    Get or create a root XML element with the specified name.

    Args:
        config: XML configuration document
        name: Name of the root element

    Returns:
        The XML element with the specified name
    """
    xml_section = config.getElementsByTagName(name)

    if len(xml_section) == 0:
        xml_section = config.createElement(name)
        config.appendChild(xml_section)
    else:
        xml_section = xml_section[0]

    return xml_section


def getSection(config: Document, xml_root: Any, name: str) -> Any:
    """
    Get or create a section XML element with the specified name.

    Args:
        config: XML configuration document
        xml_root: Root XML element
        name: Name of the section

    Returns:
        The XML element with the specified name
    """
    xml_section = xml_root.getElementsByTagName(name)

    if len(xml_section) == 0:
        xml_section = config.createElement(name)
        xml_root.appendChild(xml_section)
    else:
        xml_section = xml_section[0]

    return xml_section


def removeSection(config: Document, xml_root: Any, name: str):
    """
    Remove a section from the XML.

    Args:
        config: XML configuration document
        xml_root: Root XML element
        name: Name of the section to remove
    """
    xml_section = xml_root.getElementsByTagName(name)

    for i in range(0, len(xml_section)):
        old = xml_root.removeChild(xml_section[i])
        old.unlink()


def addCommonPlayerPorts(config: Document, xml_input: Any, nplayer: int):
    """
    Add common player ports for guns.

    Args:
        config: XML configuration document
        xml_input: Input XML element
        nplayer: Player number
    """
    # adstick for guns
    for axis in ["X", "Y"]:
        nanalog = 1 if axis == "X" else 2
        xml_port = config.createElement("port")
        xml_port.setAttribute("tag", f":mainpcb:ANALOG{nanalog}")
        xml_port.setAttribute("type", f"P{nplayer}_AD_STICK_{axis}")
        xml_port.setAttribute("mask", "255")
        xml_port.setAttribute("defvalue", "128")
        xml_newseq = config.createElement("newseq")
        xml_newseq.setAttribute("type", "standard")
        xml_port.appendChild(xml_newseq)
        value = config.createTextNode(f"GUNCODE_{nplayer}_{axis}AXIS")
        xml_newseq.appendChild(value)
        xml_input.appendChild(xml_port)
