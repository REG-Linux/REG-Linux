def setDuckstationControllers(
    duckstatonConfig, system, metadata, guns, playersControllers
):
    ## [ControllerPorts]
    if not duckstatonConfig.has_section("ControllerPorts"):
        duckstatonConfig.add_section("ControllerPorts")
    duckstatonConfig.set("ControllerPorts", "ControllerSettingsMigrated", "true")
    duckstatonConfig.set("ControllerPorts", "MultitapMode", "Disabled")
    duckstatonConfig.set("ControllerPorts", "PointerXScale", "8")
    duckstatonConfig.set("ControllerPorts", "PointerYScale", "8")
    duckstatonConfig.set("ControllerPorts", "PointerXInvert", "false")
    duckstatonConfig.set("ControllerPorts", "PointerYInvert", "false")

    if not duckstatonConfig.has_section("InputSources"):
        duckstatonConfig.add_section("InputSources")
    duckstatonConfig.set("InputSources", "SDL", "true")
    duckstatonConfig.set("InputSources", "SDLControllerEnhancedMode", "false")
    duckstatonConfig.set("InputSources", "Evdev", "false")
    duckstatonConfig.set("InputSources", "XInput", "false")
    duckstatonConfig.set("InputSources", "RawInput", "false")

    ## [Pad]
    # Clear existing Pad(x) configs
    for i in range(1, 9):
        if duckstatonConfig.has_section("Pad" + str(i)):
            duckstatonConfig.remove_section("Pad" + str(i))
    # Now create Pad1 - 8 None to start
    for i in range(1, 9):
        duckstatonConfig.add_section("Pad" + str(i))
        duckstatonConfig.set("Pad" + str(i), "Type", "None")
    # Start with mutitap disabled
    duckstatonConfig.set("ControllerPorts", "MultitapMode", "Disabled")
    # Now add the controller config based on the ES type & number connected
    nplayer = 1
    for _, pad in sorted(playersControllers.items()):
        if nplayer <= 8:
            # automatically add the multi-tap
            if nplayer > 2:
                duckstatonConfig.set("ControllerPorts", "MultitapMode", "Port1Only")
                if nplayer > 4:
                    duckstatonConfig.set("ControllerPorts", "MultitapMode", "BothPorts")
            pad_num = f"Pad{nplayer}"
            gun_num = f"Pointer-{pad.index}"
            sdl_num = f"SDL-{pad.index}"
            ctrl_num = "Controller" + str(nplayer)
            # SDL2 configs are always the same for controllers
            if system.isOptSet("duckstation_" + ctrl_num):
                duckstatonConfig.set(
                    pad_num, "Type", system.config["duckstation_" + ctrl_num]
                )
            else:
                duckstatonConfig.set(pad_num, "Type", "DigitalController")
            duckstatonConfig.set(pad_num, "Up", sdl_num + "/DPadUp")
            duckstatonConfig.set(pad_num, "Right", sdl_num + "/DPadRight")
            duckstatonConfig.set(pad_num, "Down", sdl_num + "/DPadDown")
            duckstatonConfig.set(pad_num, "Left", sdl_num + "/DPadLeft")
            duckstatonConfig.set(pad_num, "Triangle", sdl_num + "/Y")
            duckstatonConfig.set(pad_num, "Circle", sdl_num + "/B")
            duckstatonConfig.set(pad_num, "Cross", sdl_num + "/A")
            duckstatonConfig.set(pad_num, "Square", sdl_num + "/X")
            duckstatonConfig.set(pad_num, "Select", sdl_num + "/Back")
            duckstatonConfig.set(pad_num, "Start", sdl_num + "/Start")
            duckstatonConfig.set(pad_num, "L1", sdl_num + "/LeftShoulder")
            duckstatonConfig.set(pad_num, "R1", sdl_num + "/RightShoulder")
            duckstatonConfig.set(pad_num, "L2", sdl_num + "/+LeftTrigger")
            duckstatonConfig.set(pad_num, "R2", sdl_num + "/+RightTrigger")
            duckstatonConfig.set(pad_num, "L3", sdl_num + "/LeftStick")
            duckstatonConfig.set(pad_num, "R3", sdl_num + "/RightStick")
            duckstatonConfig.set(pad_num, "LLeft", sdl_num + "/-LeftX")
            duckstatonConfig.set(pad_num, "LRight", sdl_num + "/+LeftX")
            duckstatonConfig.set(pad_num, "LDown", sdl_num + "/+LeftY")
            duckstatonConfig.set(pad_num, "LUp", sdl_num + "/-LeftY")
            duckstatonConfig.set(pad_num, "RLeft", sdl_num + "/-RightX")
            duckstatonConfig.set(pad_num, "RRight", sdl_num + "/+RightX")
            duckstatonConfig.set(pad_num, "RDown", sdl_num + "/+RightY")
            duckstatonConfig.set(pad_num, "RUp", sdl_num + "/-RightY")
            duckstatonConfig.set(pad_num, "SmallMotor", sdl_num + "/SmallMotor")
            duckstatonConfig.set(pad_num, "LargeMotor", sdl_num + "/LargeMotor")
            duckstatonConfig.set(pad_num, "VibrationBias", "8")
            # D-Pad to Joystick
            if system.isOptSet("duckstation_digitalmode"):
                duckstatonConfig.set(
                    pad_num,
                    "AnalogDPadInDigitalMode",
                    system.config["duckstation_digitalmode"],
                )
                if (
                    system.isOptSet("duckstation_" + ctrl_num)
                    and system.config["duckstation_" + ctrl_num] == "AnalogController"
                ):
                    duckstatonConfig.set(pad_num, "Analog", sdl_num + "/Guide")
            else:
                duckstatonConfig.set(pad_num, "AnalogDPadInDigitalMode", "false")
            # NeGcon ?
            if (
                system.isOptSet("duckstation_" + ctrl_num)
                and system.config["duckstation_" + ctrl_num] == "NeGcon"
            ):
                duckstatonConfig.set(pad_num, "A", sdl_num + "/B")
                duckstatonConfig.set(pad_num, "B", sdl_num + "/Y")
                duckstatonConfig.set(pad_num, "I", sdl_num + "/+RightTrigger")
                duckstatonConfig.set(pad_num, "II", sdl_num + "/+LeftTrigger")
                duckstatonConfig.set(pad_num, "L", sdl_num + "/LeftShoulder")
                duckstatonConfig.set(pad_num, "R", sdl_num + "/RightShoulder")
                duckstatonConfig.set(pad_num, "SteeringLeft", sdl_num + "/-LeftX")
                duckstatonConfig.set(pad_num, "SteeringRight", sdl_num + "/+LeftX")
            # Guns
            if (
                system.isOptSet("use_guns")
                and system.getOptBoolean("use_guns")
                and len(guns) > 0
            ):
                # Justifier compatible ROM...
                if "gun_type" in metadata and metadata["gun_type"] == "justifier":
                    duckstatonConfig.set(pad_num, "Type", "Justifier")
                    duckstatonConfig.set(pad_num, "Trigger", gun_num + "/LeftButton")
                    duckstatonConfig.set(pad_num, "Start", gun_num + "/RightButton")
                # Default or GunCon compatible ROM...
                else:
                    duckstatonConfig.set(pad_num, "Type", "GunCon")
                    duckstatonConfig.set(pad_num, "Trigger", gun_num + "/LeftButton")

                ### find a keyboard key to simulate the action of the player (always like button 2) ; search in system.conf, else default config
                pedalsKeys = {1: "c", 2: "v", 3: "b", 4: "n"}
                pedalkey = None
                pedalcname = f"controllers.pedals{nplayer}"
                if pedalcname in system.config:
                    pedalkey = system.config[pedalcname]
                else:
                    if nplayer in pedalsKeys:
                        pedalkey = pedalsKeys[nplayer]
                if pedalkey is None:
                    duckstatonConfig.set(pad_num, "A", gun_num + "/RightButton")
                else:
                    duckstatonConfig.set(
                        pad_num,
                        "A",
                        gun_num + "/RightButton & Keyboard/" + pedalkey.upper(),
                    )
                ###
                duckstatonConfig.set(pad_num, "B", gun_num + "/MiddleButton")
                if (
                    system.isOptSet("duckstation_" + ctrl_num)
                    and system.config["duckstation_" + ctrl_num] == "GunCon"
                ):
                    duckstatonConfig.set(pad_num, "Trigger", sdl_num + "/+RightTrigger")
                    duckstatonConfig.set(
                        pad_num, "ShootOffscreen", sdl_num + "/+LeftTrigger"
                    )
                    duckstatonConfig.set(pad_num, "A", sdl_num + "/A")
                    duckstatonConfig.set(pad_num, "B", sdl_num + "/B")
            # Guns crosshair
            if system.isOptSet("duckstation_crosshair"):
                duckstatonConfig.set(
                    pad_num, "CrosshairScale", system.config["duckstation_crosshair"]
                )
            else:
                duckstatonConfig.set(pad_num, "CrosshairScale", "0")
            # Mouse
            if (
                system.isOptSet("duckstation_" + ctrl_num)
                and system.config["duckstation_" + ctrl_num] == "PlayStationMouse"
            ):
                duckstatonConfig.set(pad_num, "Right", sdl_num + "/B")
                duckstatonConfig.set(pad_num, "Left", sdl_num + "/A")
                duckstatonConfig.set(pad_num, "RelativeMouseMode", sdl_num + "true")
        # Next controller
        nplayer += 1

    ## [Hotkeys]
    if not duckstatonConfig.has_section("Hotkeys"):
        duckstatonConfig.add_section("Hotkeys")
    # Force defaults to be aligned with evmapy
    duckstatonConfig.set("Hotkeys", "FastForward", "Keyboard/Tab")
    duckstatonConfig.set("Hotkeys", "Reset", "Keyboard/F6")
    duckstatonConfig.set("Hotkeys", "LoadSelectedSaveState", "Keyboard/F1")
    duckstatonConfig.set("Hotkeys", "SaveSelectedSaveState", "Keyboard/F2")
    duckstatonConfig.set("Hotkeys", "SelectPreviousSaveStateSlot", "Keyboard/F3")
    duckstatonConfig.set("Hotkeys", "SelectNextSaveStateSlot", "Keyboard/F4")
    duckstatonConfig.set("Hotkeys", "Screenshot", "Keyboard/F10")
    duckstatonConfig.set("Hotkeys", "Rewind", "Keyboard/F5")
    duckstatonConfig.set("Hotkeys", "OpenPauseMenu", "Keyboard/F7")
    duckstatonConfig.set("Hotkeys", "ChangeDisc", "Keyboard/F8")
    if duckstatonConfig.has_option("Hotkeys", "OpenQuickMenu"):
        duckstatonConfig.remove_option("Hotkeys", "OpenQuickMenu")
