from csv import reader
from os import chdir, listdir, makedirs, path, symlink, unlink
from pathlib import Path
from shutil import copy2, rmtree
from typing import Any
from xml.etree.ElementTree import parse

from configgen.Command import Command
from configgen.generators.Generator import Generator
from configgen.utils.logger import get_logger
from configgen.utils.videoMode import getScreensInfos

from ...bezel.mame_bezel_manager import setup_mame_bezels

logger = get_logger(__name__)


class MameGenerator(Generator):
    """MAME Generator for creating command arrays and configurations for MAME/MESS emulators."""

    # TODO MAME requires a wayland compositor *if* bgfx is used
    def requiresWayland(self) -> bool:
        """Indicates if the generator requires Wayland compositor."""
        return True

    def supportsInternalBezels(self) -> bool:
        """Indicates if the generator supports internal bezels."""
        return True

    def generate(
        self,
        system: Any,
        rom: str,
        players_controllers: Any,
        metadata: Any,
        guns: Any,
        wheels: Any,
        game_resolution: dict[str, Any],
    ) -> Command:
        """
        Generate the MAME command array for the specified ROM and system configuration.

        Args:
            system: System configuration
            rom: Path to the ROM file
            players_controllers: Controller configuration for players
            metadata: Game metadata
            guns: Light gun configuration
            wheels: Steering wheel configuration
            game_resolution: Dictionary containing game resolution information

        Returns:
            Command object with the appropriate MAME command array
        """
        # Extract "<romfile.zip>"
        romBasename = path.basename(rom)
        romDirname = path.dirname(rom)
        (romName, romExt) = path.splitext(romBasename)

        softDir = "/var/run/mame_software/"
        softList = ""
        messModel = ""
        subdirSoftList = ["mac_hdd", "bbc_hdd", "cdi", "archimedes_hdd", "fmtowns_cd"]

        # Generate userdata folders if needed
        mamePaths = [
            "system/configs/mame",
            "saves/mame",
            "saves/mame/nvram",
            "saves/mame/cfg",
            "saves/mame/input",
            "saves/mame/state",
            "saves/mame/diff",
            "saves/mame/comments",
            "bios/mame",
            "bios/mame/artwork",
            "cheats/mame",
            "saves/mame/plugins",
            "system/configs/mame/ctrlr",
            "system/configs/mame/ini",
            "bios/mame/artwork/crosshairs",
        ]
        for checkPath in mamePaths:
            if not path.exists("/userdata/" + checkPath + "/"):
                makedirs("/userdata/" + checkPath + "/")

        messDataFile = "/usr/share/reglinux/configgen/data/mame/messSystems.csv"
        openFile = open(messDataFile)
        messSystems = []
        messSysName = []
        messRomType = []
        messAutoRun = []
        with openFile:
            messDataList = reader(openFile, delimiter=";", quotechar="'")
            for row in messDataList:
                messSystems.append(row[0])
                messSysName.append(row[1])
                messRomType.append(row[2])
                messAutoRun.append(row[3])

        # Identify the current system
        try:
            messMode = messSystems.index(system.name)
        except ValueError:
            messMode = -1

        if system.isOptSet("softList") and system.config["softList"] != "none":
            softList = system.config["softList"]
        else:
            softList = ""

        # Auto softlist for FM Towns if there is a zip that matches the folder name
        # Used for games that require a CD and floppy to both be inserted
        if system.name == "fmtowns" and softList == "":
            romParentPath = path.basename(romDirname)
            if path.exists(f"/userdata/roms/fmtowns/{romParentPath}.zip"):
                softList = "fmtowns_cd"

        command_array = ["/usr/bin/mame/mame"]
        # MAME options used here are explained as it's not always straightforward
        # A lot more options can be configured, just run mame -showusage and have a look
        command_array += ["-skip_gameinfo"]
        if messMode == -1:
            command_array += [
                "-rompath",
                romDirname + ";/userdata/bios/mame/;/userdata/bios/",
            ]
        else:
            if softList in subdirSoftList:
                command_array += [
                    "-rompath",
                    romDirname
                    + ";/userdata/bios/mame/;/userdata/bios/;/userdata/roms/mame/;/var/run/mame_software/",
                ]
            else:
                command_array += [
                    "-rompath",
                    romDirname
                    + ";/userdata/bios/mame/;/userdata/bios/;/userdata/roms/mame/",
                ]

        # MAME various paths we can probably do better
        command_array += [
            "-bgfx_path",
            "/usr/bin/mame/bgfx/",
        ]  # Core bgfx files can be left on ROM filesystem
        command_array += [
            "-fontpath",
            "/usr/bin/mame/",
        ]  # Fonts can be left on ROM filesystem
        command_array += [
            "-languagepath",
            "/usr/bin/mame/language/",
        ]  # Translations can be left on ROM filesystem
        command_array += [
            "-pluginspath",
            "/usr/bin/mame/plugins/;/userdata/saves/mame/plugins",
        ]
        command_array += [
            "-samplepath",
            "/userdata/bios/mame/samples/",
        ]  # Current reglinux storage location for MAME samples
        command_array += [
            "-artpath",
            "/var/run/mame_artwork/;/usr/bin/mame/artwork/;/userdata/bios/mame/artwork/;/userdata/decorations/",
        ]  # first for systems ; second for overlays

        # Enable cheats
        command_array += ["-cheat"]
        command_array += [
            "-cheatpath",
            "/userdata/cheats/mame/",
        ]  # Should this point to path containing the cheat.7z file

        # logs
        command_array += ["-verbose"]

        # MAME saves a lot of stuff, we need to map this on /userdata/saves/mame/<subfolder> for each one
        command_array += ["-nvram_directory", "/userdata/saves/mame/nvram/"]

        # Set custom config path if option is selected or default path if not
        if system.isOptSet("customcfg"):
            customCfg = system.getOptBoolean("customcfg")
        else:
            customCfg = False

        if system.name == "mame":
            if customCfg:
                cfgPath = "/userdata/system/configs/mame/custom/"
            else:
                cfgPath = "/userdata/system/configs/mame/"
            if not path.exists("/userdata/system/configs/mame/"):
                makedirs("/userdata/system/configs/mame/")
        else:
            if customCfg:
                cfgPath = (
                    "/userdata/system/configs/mame/"
                    + messSysName[messMode]
                    + "/custom/"
                )
            else:
                cfgPath = "/userdata/system/configs/mame/" + messSysName[messMode] + "/"
            if not path.exists(
                "/userdata/system/configs/mame/" + messSysName[messMode] + "/"
            ):
                makedirs("/userdata/system/configs/mame/" + messSysName[messMode] + "/")
        if not path.exists(cfgPath):
            makedirs(cfgPath)

        # MAME will create custom configs per game for MAME ROMs and MESS ROMs with no system attached (LCD games, TV games, etc.)
        # This will allow an alternate config path per game for MESS console/computer ROMs that may need additional config.
        if system.isOptSet("pergamecfg") and system.getOptBoolean("pergamecfg"):
            if not messMode == -1:
                if not messSysName[messMode] == "":
                    if not path.exists(
                        "/userdata/system/configs/mame/" + messSysName[messMode] + "/"
                    ):
                        makedirs(
                            "/userdata/system/configs/mame/"
                            + messSysName[messMode]
                            + "/"
                        )
                    cfgPath = (
                        "/userdata/system/configs/mame/"
                        + messSysName[messMode]
                        + "/"
                        + romBasename
                        + "/"
                    )
                    if not path.exists(cfgPath):
                        makedirs(cfgPath)
        command_array += ["-cfg_directory", cfgPath]
        command_array += ["-input_directory", "/userdata/saves/mame/input/"]
        command_array += ["-state_directory", "/userdata/saves/mame/state/"]
        command_array += ["-snapshot_directory", "/userdata/screenshots/"]
        command_array += ["-diff_directory", "/userdata/saves/mame/diff/"]
        command_array += ["-comment_directory", "/userdata/saves/mame/comments/"]
        command_array += ["-homepath", "/userdata/saves/mame/plugins/"]
        command_array += ["-ctrlrpath", "/userdata/system/configs/mame/ctrlr/"]
        command_array += [
            "-inipath",
            "/userdata/system/configs/mame/;/userdata/system/configs/mame/ini/",
        ]
        command_array += ["-crosshairpath", "/userdata/bios/mame/artwork/crosshairs/"]
        if softList != "":
            command_array += ["-swpath", softDir]
            command_array += ["-hashpath", softDir + "hash/"]

        # TODO These paths are not handled yet
        # TODO -swpath              path to loose software - might use if we want software list MESS support

        # BGFX video engine : https://docs.mamedev.org/advanced/bgfx.html
        if system.isOptSet("video") and system.config["video"] == "bgfx":
            command_array += ["-video", "bgfx"]

            # BGFX backend
            if (
                system.isOptSet("bgfxbackend")
                and system.config["bgfxbackend"] != "automatic"
            ):
                command_array += ["-bgfx_backend", system.config["bgfxbackend"]]
            else:
                command_array += ["-bgfx_backend", "auto"]

            # BGFX shaders effects
            if (
                system.isOptSet("bgfxshaders")
                and system.config["bgfxshaders"] != "default"
            ):
                command_array += ["-bgfx_screen_chains", system.config["bgfxshaders"]]
            else:
                command_array += ["-bgfx_screen_chains", "default"]

        # Other video modes
        elif system.isOptSet("video") and system.config["video"] == "accel":
            command_array += ["-video", "accel"]
        else:
            command_array += ["-video", "opengl"]

        # CRT / SwitchRes support
        if system.isOptSet("switchres") and system.getOptBoolean("switchres"):
            command_array += ["-modeline_generation"]
            command_array += ["-changeres"]
            command_array += ["-modesetting"]
            command_array += ["-readconfig"]
        else:
            command_array += [
                "-resolution",
                "{}x{}".format(game_resolution["width"], game_resolution["height"]),
            ]

        # Refresh rate options to help with screen tearing
        # syncrefresh is unlisted, it requires specific display timings and 99.9% of users will get unplayable games.
        # Leaving it so it can be set manually, for CRT or other arcade-specific display users.
        if system.isOptSet("vsync") and system.getOptBoolean("vsync"):
            command_array += ["-waitvsync"]
        if system.isOptSet("syncrefresh") and system.getOptBoolean("syncrefresh"):
            command_array += ["-syncrefresh"]

        # Rotation / TATE options
        if system.isOptSet("rotation") and system.config["rotation"] == "autoror":
            command_array += ["-autoror"]
        if system.isOptSet("rotation") and system.config["rotation"] == "autorol":
            command_array += ["-autorol"]

        # Artwork crop
        if system.isOptSet("artworkcrop") and system.getOptBoolean("artworkcrop"):
            command_array += ["-artwork_crop"]

        # UI enable - for computer systems, the default sends all keys to the emulated system.
        # This will enable hotkeys, but some keys may pass through to MAME and not be usable in the emulated system.
        # Hotkey + D-Pad Up will toggle this when in use (scroll lock key)
        if not (system.isOptSet("enableui") and not system.getOptBoolean("enableui")):
            command_array += ["-ui_active"]

        # Load selected plugins
        pluginsToLoad = []
        if not (
            system.isOptSet("hiscoreplugin")
            and not system.getOptBoolean("hiscoreplugin")
        ):
            pluginsToLoad += ["hiscore"]
        if system.isOptSet("coindropplugin") and system.getOptBoolean("coindropplugin"):
            pluginsToLoad += ["coindrop"]
        if system.isOptSet("dataplugin") and system.getOptBoolean("dataplugin"):
            pluginsToLoad += ["data"]
        if len(pluginsToLoad) > 0:
            command_array += ["-plugins", "-plugin", ",".join(pluginsToLoad)]

        # Mouse
        if (system.isOptSet("use_mouse") and system.getOptBoolean("use_mouse")) or not (
            messSysName[messMode] == "" or messMode == -1
        ):
            command_array += ["-dial_device", "mouse"]
            command_array += ["-trackball_device", "mouse"]
            command_array += ["-paddle_device", "mouse"]
            command_array += ["-positional_device", "mouse"]
            command_array += ["-mouse_device", "mouse"]
            command_array += ["-ui_mouse"]
            if not (system.isOptSet("use_guns") and system.getOptBoolean("use_guns")):
                command_array += ["-lightgun_device", "mouse"]
                command_array += ["-adstick_device", "mouse"]
        else:
            command_array += ["-dial_device", "joystick"]
            command_array += ["-trackball_device", "joystick"]
            command_array += ["-paddle_device", "joystick"]
            command_array += ["-positional_device", "joystick"]
            command_array += ["-mouse_device", "joystick"]
            if not (system.isOptSet("use_guns") and system.getOptBoolean("use_guns")):
                command_array += ["-lightgun_device", "joystick"]
                command_array += ["-adstick_device", "joystick"]
        # Multimouse option currently hidden in ES, SDL only detects one mouse.
        # Leaving code intact for testing & possible ManyMouse integration
        if system.isOptSet("multimouse") and system.getOptBoolean("multimouse"):
            command_array += ["-multimouse"]

        # guns
        if system.isOptSet("use_guns") and system.getOptBoolean("use_guns"):
            command_array += ["-lightgunprovider", "udev"]
            command_array += ["-lightgun_device", "lightgun"]
            command_array += ["-adstick_device", "lightgun"]
        if system.isOptSet("offscreenreload") and system.getOptBoolean(
            "offscreenreload"
        ):
            command_array += ["-offscreen_reload"]

        # wheels
        # The 'wheels' variable was unused, and the 'pass' statement for system.isOptSet("use_wheels") is unnecessary.
        # If 'use_wheels' is set and true, no MAME arguments are added here, so the block can be removed.

        if system.isOptSet("multiscreens") and system.getOptBoolean("multiscreens"):
            screens = getScreensInfos(system.config)
            if len(screens) > 1:
                command_array += ["-numscreens", str(len(screens))]

        # Finally we pass game name
        # MESS will use the full filename and pass the system & rom type parameters if needed.
        if messSysName[messMode] == "" or messMode == -1:
            command_array += [romBasename]
        else:
            messModel = messSysName[messMode]
            # Alternate system for machines that have different configs (ie computers with different hardware)
            if system.isOptSet("altmodel"):
                messModel = system.config["altmodel"]
            command_array += [messModel]

            # TI-99 32k RAM expansion & speech modules - enabled by default
            if system.name == "ti99":
                command_array += ["-ioport", "peb"]
                if not system.isOptSet("ti99_32kram") or (
                    system.isOptSet("ti99_32kram")
                    and system.getOptBoolean("ti99_32kram")
                ):
                    command_array += ["-ioport:peb:slot2", "32kmem"]
                if not system.isOptSet("ti99_speech") or (
                    system.isOptSet("ti99_speech")
                    and system.getOptBoolean("ti99_speech")
                ):
                    command_array += ["-ioport:peb:slot3", "speech"]

            # Laser 310 Memory Expansion & Joystick
            if system.name == "laser310":
                command_array += ["-io", "joystick"]
                if not system.isOptSet("memslot"):
                    laser310mem = "laser_64k"
                else:
                    laser310mem = system.config["memslot"]
                command_array += ["-mem", laser310mem]

            # BBC Joystick
            if system.name == "bbc":
                if (
                    system.isOptSet("sticktype")
                    and system.config["sticktype"] != "none"
                ):
                    command_array += ["-analogue", system.config["sticktype"]]

            # Apple II
            if system.name == "apple2":
                command_array += ["-sl7", "cffa202"]
                if system.isOptSet("gameio") and system.config["gameio"] != "none":
                    if system.config["gameio"] == "joyport" and messModel != "apple2p":
                        logger.debug(
                            "Joyport joystick is only compatible with Apple II Plus"
                        )
                    else:
                        command_array += ["-gameio", system.config["gameio"]]

            # RAM size (Mac excluded, special handling below)
            if system.name != "macintosh" and system.isOptSet("ramsize"):
                command_array += ["-ramsize", str(system.config["ramsize"]) + "M"]

            # Mac RAM & Image Reader (if applicable)
            if system.name == "macintosh":
                if system.isOptSet("ramsize"):
                    ramSize = int(system.config["ramsize"])
                    if messModel in ["maciix", "maclc3"]:
                        if messModel == "maclc3" and ramSize == 2:
                            ramSize = 4
                        if messModel == "maclc3" and ramSize > 80:
                            ramSize = 80
                        if messModel == "maciix" and ramSize == 16:
                            ramSize = 32
                        if messModel == "maciix" and ramSize == 48:
                            ramSize = 64
                        command_array += ["-ramsize", str(ramSize) + "M"]
                    if messModel == "maciix":
                        imageSlot = "nba"
                        if system.isOptSet("imagereader"):
                            if system.config["imagereader"] == "disabled":
                                imageSlot = ""
                            else:
                                imageSlot = system.config["imagereader"]
                        if imageSlot != "":
                            command_array += ["-" + imageSlot, "image"]

            if softList == "":
                # Boot disk for Macintosh
                # Will use Floppy 1 or Hard Drive, depending on the disk.
                if system.name == "macintosh" and system.isOptSet("bootdisk"):
                    if system.config["bootdisk"] in [
                        "macos30",
                        "macos608",
                        "macos701",
                        "macos75",
                    ]:
                        bootType = "-flop1"
                        bootDisk = (
                            "/userdata/bios/" + system.config["bootdisk"] + ".img"
                        )
                    else:
                        bootType = "-hard"
                        bootDisk = (
                            "/userdata/bios/" + system.config["bootdisk"] + ".chd"
                        )
                    command_array += [bootType, bootDisk]

                # Alternate ROM type for systems with mutiple media (ie cassette & floppy)
                # Mac will auto change floppy 1 to 2 if a boot disk is enabled
                # Only one drive on FMTMarty
                if system.name != "macintosh":
                    if system.isOptSet("altromtype"):
                        if (
                            messModel == "fmtmarty"
                            and system.config["altromtype"] == "flop1"
                        ):
                            command_array += ["-flop"]
                        else:
                            command_array += ["-" + system.config["altromtype"]]
                    elif system.name == "adam":
                        # add some logic based on the rom extension
                        rom_extension = path.splitext(rom)[1].lower()
                        if rom_extension == ".ddp":
                            command_array += ["-cass1"]
                        elif rom_extension == ".dsk":
                            command_array += ["-flop1"]
                        else:
                            command_array += ["-cart1"]
                    elif system.name == "coco":
                        if romExt.casefold() == ".cas":
                            command_array += ["-cass"]
                        elif romExt.casefold() == ".dsk":
                            command_array += ["-flop1"]
                        else:
                            command_array += ["-cart"]
                    else:
                        command_array += ["-" + messRomType[messMode]]
                else:
                    if system.isOptSet("bootdisk"):
                        if (
                            (
                                system.isOptSet("altromtype")
                                and system.config["altromtype"] == "flop1"
                            )
                            or not system.isOptSet("altromtype")
                        ) and system.config["bootdisk"] in [
                            "macos30",
                            "macos608",
                            "macos701",
                            "macos75",
                        ]:
                            command_array += ["-flop2"]
                        elif system.isOptSet("altromtype"):
                            command_array += ["-" + system.config["altromtype"]]
                        else:
                            command_array += ["-" + messRomType[messMode]]
                    else:
                        if system.isOptSet("altromtype"):
                            command_array += ["-" + system.config["altromtype"]]
                        else:
                            command_array += ["-" + messRomType[messMode]]
                # Use the full filename for MESS ROMs
                command_array += [rom]
            else:
                # Prepare software lists
                if softList != "":
                    if not path.exists(softDir):
                        makedirs(softDir)
                    for file_name in listdir(softDir):
                        checkFile = path.join(softDir, file_name)
                        if path.islink(checkFile):
                            unlink(checkFile)
                        if path.isdir(checkFile):
                            rmtree(checkFile)
                    if not path.exists(softDir + "hash/"):
                        makedirs(softDir + "hash/")
                    # Clear existing hashfile links
                    for hashFile in listdir(softDir + "hash/"):
                        if hashFile.endswith(".xml"):
                            unlink(softDir + "hash/" + hashFile)
                    symlink(
                        "/usr/bin/mame/hash/" + softList + ".xml",
                        softDir + "hash/" + softList + ".xml",
                    )
                    if softList in subdirSoftList:
                        romPath = Path(romDirname)
                        symlink(str(romPath.parents[0]), softDir + softList, True)
                        command_array += [path.basename(romDirname)]
                    else:
                        symlink(romDirname, softDir + softList, True)
                        command_array += [path.splitext(romBasename)[0]]

            # Create & add a blank disk if needed, insert into drive 2
            # or drive 1 if drive 2 is selected manually or FM Towns Marty.
            if system.isOptSet("addblankdisk") and system.getOptBoolean("addblankdisk"):
                blankDisk = None
                targetFolder = None
                targetDisk = None
                if system.name == "fmtowns":
                    blankDisk = "/usr/share/mame/blank.fmtowns"
                    targetFolder = f"/userdata/saves/mame/{system.name}"
                    targetDisk = f"{targetFolder}/{path.splitext(romBasename)[0]}.fmtowns"
                # Add elif statements here for other systems if enabled
                if (
                    blankDisk is not None
                    and targetFolder is not None
                    and targetDisk is not None
                ):
                    if not path.exists(targetFolder):
                        makedirs(targetFolder)
                    if not path.exists(targetDisk):
                        copy2(blankDisk, targetDisk)
                    # Add other single floppy systems to this if statement
                    if messModel == "fmtmarty":
                        command_array += ["-flop", targetDisk]
                    elif (
                        system.isOptSet("altromtype")
                        and system.config["altromtype"] == "flop2"
                    ):
                        command_array += ["-flop1", targetDisk]
                    else:
                        command_array += ["-flop2", targetDisk]

            autoRunCmd = ""
            autoRunDelay = 0
            # Autostart computer games where applicable
            # bbc has different boots for floppy & cassette, no special boot for carts
            if system.name == "bbc":
                if system.isOptSet("altromtype") or softList != "":
                    if (
                        system.isOptSet("altromtype")
                        and system.config["altromtype"] == "cass"
                    ) or softList.endswith("cass"):
                        autoRunCmd = '*tape\\nchain""\\n'
                        autoRunDelay = 2
                    elif (
                        system.isOptSet("altromtype")
                        and system.config["altromtype"].startswith("flop")
                    ) or softList.endswith("flop"):
                        autoRunCmd = "*cat\\n\\n\\n\\n*exec !boot\\n"
                        autoRunDelay = 3
                else:
                    autoRunCmd = "*cat\\n\\n\\n\\n*exec !boot\\n"
                    autoRunDelay = 3
            # fm7 boots floppies, needs cassette loading
            elif system.name == "fm7":
                if system.isOptSet("altromtype") or softList != "":
                    if (
                        system.isOptSet("altromtype")
                        and system.config["altromtype"] == "cass"
                    ) or softList.endswith("cass"):
                        autoRunCmd = "LOADM”“,,R\\n"
                        autoRunDelay = 5
            elif system.name == "coco":
                rom_type = "cart"
                autoRunDelay = 2

                # if using software list, use "usage" for autoRunCmd (if provided)
                if softList != "":
                    softListFile = f"/usr/bin/mame/hash/{softList}.xml"
                    if path.exists(softListFile):
                        softwarelist = parse(softListFile)
                        for software in softwarelist.findall("software"):
                            if software.attrib != {}:
                                if software.get("name") == romName:
                                    for info in software.iter("info"):
                                        if info.get("name") == "usage":
                                            autoRunCmd = info.get("value")

                # if still undefined, default autoRunCmd based on media type
                if autoRunCmd == "":
                    if (
                        (
                            system.isOptSet("altromtype")
                            and system.config["altromtype"] == "cass"
                        )
                        or (softList != "" and softList.endswith("cass"))
                        or romExt.casefold() == ".cas"
                    ):
                        rom_type = "cass"
                        if romName.casefold().endswith(".bas"):
                            autoRunCmd = "CLOAD:RUN\\n"
                        else:
                            autoRunCmd = "CLOADM:EXEC\\n"
                    if (
                        (
                            system.isOptSet("altromtype")
                            and system.config["altromtype"] == "flop1"
                        )
                        or (softList != "" and softList.endswith("flop"))
                        or romExt.casefold() == ".dsk"
                    ):
                        rom_type = "flop"
                        if romName.casefold().endswith(".bas"):
                            autoRunCmd = f'RUN "{romName}"\\n'
                        else:
                            autoRunCmd = f'LOADM "{romName}":EXEC\\n'

                # check for a user override
                autoRunFile = f"system/configs/mame/autoload/{system.name}_{rom_type}_autoload.csv"
                if path.exists(autoRunFile):
                    openARFile = open(autoRunFile)
                    with openARFile:
                        autoRunList = reader(openARFile, delimiter=";", quotechar="'")
                        for row in autoRunList:
                            if row and not row[0].startswith("#"):
                                if row[0].casefold() == romName.casefold():
                                    autoRunCmd = row[1] + "\\n"
            else:
                # Check for an override file, otherwise use generic (if it exists)
                autoRunCmd = messAutoRun[messMode]
                autoRunFile = (
                    f"/usr/share/reglinux/configgen/data/mame/{softList}_autoload.csv"
                )
                if path.exists(autoRunFile):
                    openARFile = open(autoRunFile)
                    with openARFile:
                        autoRunList = reader(openARFile, delimiter=";", quotechar="'")
                        for row in autoRunList:
                            if (
                                row[0].casefold()
                                == path.splitext(romBasename)[0].casefold()
                            ):
                                autoRunCmd = row[1]
                                autoRunDelay = 3
            if autoRunCmd is not None:
                if autoRunCmd.startswith("'"):
                    autoRunCmd = autoRunCmd.replace("'", "")
                command_array += [
                    "-autoboot_delay",
                    str(autoRunDelay),
                    "-autoboot_command",
                    autoRunCmd,
                ]

        # Setup MAME bezels
        messSysNameForBezel = (
            messSysName[messMode] if messMode != -1 else rom
        )  # Pass ROM name for MAME games, system name for MESS games
        setup_mame_bezels(system, rom, messSysNameForBezel, game_resolution, guns)

        # Change directory to MAME folder (allows data plugin to load properly)
        chdir("/usr/bin/mame")
        return Command(array=command_array, env={"PWD": "/usr/bin/mame/"})

    @staticmethod
    def getRoot(config: Any, name: str) -> Any:
        """
        Get or create an XML root element with the specified name.

        Args:
            config: XML configuration document
            name: Name of the root element to get or create

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

    @staticmethod
    def getSection(config: Any, xml_root: Any, name: str) -> Any:
        """
        Get or create an XML section element with the specified name.

        Args:
            config: XML configuration document
            xml_root: XML root element
            name: Name of the section element to get or create

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

    @staticmethod
    def removeSection(xml_root: Any, name: str) -> None:
        """
        Remove XML section elements with the specified name.

        Args:
            xml_root: XML root element containing sections to remove
            name: Name of the section elements to remove
        """
        xml_section = xml_root.getElementsByTagName(name)

        for i in range(0, len(xml_section)):
            old = xml_root.removeChild(xml_section[i])
            old.unlink()


def getMameControlScheme(system: Any, romBasename: str) -> str:
    """
    Determine the appropriate MAME control scheme for a given system and ROM.

    Args:
        system: System configuration
        romBasename: Name of the ROM file

    Returns:
        String representing the control scheme to use
    """
    # Game list files
    mameCapcom: str = "/usr/share/reglinux/configgen/data/mame/mameCapcom.txt"
    mameKInstinct: str = "/usr/share/reglinux/configgen/data/mame/mameKInstinct.txt"
    mameMKombat: str = "/usr/share/reglinux/configgen/data/mame/mameMKombat.txt"
    mameNeogeo: str = "/usr/share/reglinux/configgen/data/mame/mameNeogeo.txt"
    mameTwinstick: str = "/usr/share/reglinux/configgen/data/mame/mameTwinstick.txt"
    mameRotatedstick: str = (
        "/usr/share/reglinux/configgen/data/mame/mameRotatedstick.txt"
    )

    # Controls for games with 5-6 buttons or other unusual controls
    if system.isOptSet("altlayout"):
        controllerType: str = system.config["altlayout"]  # Option was manually selected
    else:
        controllerType: str = "auto"

    if controllerType in ["default", "neomini", "neocd", "twinstick", "qbert"]:
        return controllerType
    else:
        try:
            with open(mameCapcom) as f:
                capcomList: set = set(f.read().split())
            with open(mameMKombat) as f:
                mkList: set = set(f.read().split())
            with open(mameKInstinct) as f:
                kiList: set = set(f.read().split())
            with open(mameNeogeo) as f:
                neogeoList: set = set(f.read().split())
            with open(mameTwinstick) as f:
                twinstickList: set = set(f.read().split())
            with open(mameRotatedstick) as f:
                qbertList: set = set(f.read().split())
        except OSError as e:
            logger.error(f"Error reading MAME list files: {e}")
            # Initialize empty sets to avoid breaking the process
            capcomList: set = set()
            mkList: set = set()
            kiList: set = set()
            neogeoList: set = set()
            twinstickList: set = set()
            qbertList: set = set()

        romName: str = path.splitext(romBasename)[0]
        if romName in capcomList:
            if controllerType in ["auto", "snes"]:
                return "sfsnes"
            elif controllerType == "megadrive":
                return "megadrive"
            elif controllerType == "fightstick":
                return "sfstick"
        elif romName in mkList:
            if controllerType in ["auto", "snes"]:
                return "mksnes"
            elif controllerType == "megadrive":
                return "mkmegadrive"
            elif controllerType == "fightstick":
                return "mkstick"
        elif romName in kiList:
            if controllerType in ["auto", "snes"]:
                return "kisnes"
            elif controllerType == "megadrive":
                return "megadrive"
            elif controllerType == "fightstick":
                return "sfstick"
        elif romName in neogeoList:
            return "neomini"
        elif romName in twinstickList:
            return "twinstick"
        elif romName in qbertList:
            return "qbert"
        else:
            if controllerType == "fightstick":
                return "fightstick"
            if controllerType == "megadrive":
                return "mddefault"

    return "default"
