import xml.etree.ElementTree as ET
import xml.parsers.expat
from csv import reader
from os import linesep, listdir
from pathlib import Path
from shutil import copy2, rmtree
from typing import Any
from xml.dom import minidom
from zipfile import ZipFile

from configgen.utils.logger import get_logger

eslog = get_logger(__name__)

# Define RetroPad inputs for mapping
retroPad = {
    "joystick1up": "YAXIS_UP_SWITCH",
    "joystick1down": "YAXIS_DOWN_SWITCH",
    "joystick1left": "XAXIS_LEFT_SWITCH",
    "joystick1right": "XAXIS_RIGHT_SWITCH",
    "up": "HAT{0}UP",
    "down": "HAT{0}DOWN",
    "left": "HAT{0}LEFT",
    "right": "HAT{0}RIGHT",
    "joystick2up": "RYAXIS_NEG_SWITCH",
    "joystick2down": "RYAXIS_POS_SWITCH",
    "joystick2left": "RXAXIS_NEG_SWITCH",
    "joystick2right": "RXAXIS_POS_SWITCH",
    "a": "BUTTON1",
    "b": "BUTTON2",
    "x": "BUTTON3",
    "y": "BUTTON4",
    "pageup": "BUTTON5",
    "pagedown": "BUTTON6",
    "l2": "RZAXIS_POS_SWITCH",
    "r2": "ZAXIS_POS_SWITCH",
    "l3": "BUTTON12",
    "r3": "BUTTON11",
    "select": "SELECT",
    "start": "START",
}


def generateMAMEConfigs(
    playersControllers: Any,
    system: Any,
    rom: str,
    guns: Any,
) -> list[str]:
    # Generate command line for MAME
    commandLine: list[str] = []
    romBasename = Path(rom).name
    romDirname = str(Path(rom).parent)
    (romDrivername, romExt) = Path(rom).stem, Path(rom).suffix
    specialController = "none"

    if system.config["core"] in ["mame"]:
        corePath = "lr-" + system.config["core"]
    else:
        corePath = system.config["core"]

    if system.name in ["mame", "neogeo", "lcdgames", "plugnplay", "vis"]:
        # Set up command line for basic systems
        # ie. no media, softlists, etc.
        if system.getOptBoolean("customcfg"):
            cfgPath = Path("/userdata/system/configs") / corePath / "custom/"
        else:
            cfgPath = Path("/userdata/saves/mame/mame/cfg/")
        if not cfgPath.exists():
            cfgPath.mkdir(parents=True, exist_ok=True)
        if system.name == "vis":
            commandLine += ["vis", "-cdrom", f'"{rom}"']
        else:
            commandLine += [romDrivername]
        commandLine += ["-cfg_directory", str(cfgPath)]
        commandLine += [
            "-rompath",
            f"{romDirname};{Path('/userdata/bios/mame/')!s};{Path('/userdata/bios/')!s}",
        ]
        pluginsToLoad: list[str] = []
        if not (
            system.isOptSet("hiscoreplugin")
            and not system.getOptBoolean("hiscoreplugin")
        ):
            pluginsToLoad += ["hiscore"]
        if system.isOptSet("coindropplugin") and system.getOptBoolean("coindropplugin"):
            pluginsToLoad += ["coindrop"]
        if len(pluginsToLoad) > 0:
            commandLine += ["-plugins", "-plugin", ",".join(pluginsToLoad)]
        messMode = -1
        messModel = ""
    else:
        # Set up command line for MESS
        softDir = "/var/run/mame_software/"
        subdirSoftList = ["mac_hdd", "bbc_hdd", "cdi", "archimedes_hdd", "fmtowns_cd"]
        if system.isOptSet("softList") and system.config["softList"] != "none":
            softList = system.config["softList"]
        else:
            softList = ""

        # Auto softlist for FM Towns if there is a zip that matches the folder name
        # Used for games that require a CD and floppy to both be inserted
        if system.name == "fmtowns" and softList == "":
            romParentPath = Path(romDirname).name
            if (Path("/userdata/roms/fmtowns") / f"{romParentPath}.zip").exists():
                softList = "fmtowns_cd"

        # Determine MESS system name (if needed)
        messDataFile = Path("/usr/share/reglinux/configgen/data/mame/messSystems.csv")
        with Path(str(messDataFile)).open() as openFile:
            messSystems = []
            messSysName = []
            messRomType = []
            messAutoRun = []
            messDataList = reader(openFile, delimiter=";", quotechar="'")
            for row in messDataList:
                messSystems.append(row[0])
                messSysName.append(row[1])
                messRomType.append(row[2])
                messAutoRun.append(row[3])
        messMode = messSystems.index(system.name)

        # Alternate system for machines that have different configs (ie computers with different hardware)
        messModel: str = messSysName[messMode]
        if system.isOptSet("altmodel"):
            messModel = system.config["altmodel"]
        commandLine += [messModel]

        if messSysName[messMode] == "":
            # Command line for non-arcade, non-system ROMs (lcdgames, plugnplay)
            if system.getOptBoolean("customcfg"):
                cfgPath = Path("/userdata/system/configs") / corePath / "custom/"
            else:
                cfgPath = Path("/userdata/saves/mame/mame/cfg/")
            if not cfgPath.exists():
                cfgPath.mkdir(parents=True, exist_ok=True)
            commandLine += [romDrivername]
            commandLine += ["-cfg_directory", str(cfgPath)]
            commandLine += ["-rompath", f"{romDirname};{Path('/userdata/bios/')!s}"]
        else:
            # Command line for MESS consoles/computers
            # TI-99 32k RAM expansion & speech modules
            # Don't enable 32k by default
            if system.name == "ti99":
                commandLine += ["-ioport", "peb"]
                if system.isOptSet("ti99_32kram") and system.getOptBoolean(
                    "ti99_32kram",
                ):
                    commandLine += ["-ioport:peb:slot2", "32kmem"]
                if not system.isOptSet("ti99_speech") or (
                    system.isOptSet("ti99_speech")
                    and system.getOptBoolean("ti99_speech")
                ):
                    commandLine += ["-ioport:peb:slot3", "speech"]

            # Laser 310 Memory Expansion & joystick
            if system.name == "laser310":
                commandLine += ["-io", "joystick"]
                if not system.isOptSet("memslot"):
                    laser310mem = "laser_64k"
                else:
                    laser310mem = system.config["memslot"]
                commandLine += ["-mem", laser310mem]

            # BBC Joystick
            if (
                system.name == "bbc"
                and system.isOptSet("sticktype")
                and system.config["sticktype"] != "none"
            ):
                commandLine += ["-analogue", system.config["sticktype"]]
                specialController = system.config["sticktype"]

            # Apple II
            if system.name == "apple2":
                commandLine += ["-sl7", "cffa202"]
                if system.isOptSet("gameio") and system.config["gameio"] != "none":
                    if system.config["gameio"] == "joyport" and messModel != "apple2p":
                        eslog.debug("Joyport is only compatible with Apple II +")
                    else:
                        commandLine += ["-gameio", system.config["gameio"]]
                        specialController = system.config["gameio"]

            # RAM size (Mac excluded, special handling below)
            if system.name != "macintosh" and system.isOptSet("ramsize"):
                commandLine += ["-ramsize", str(system.config["ramsize"]) + "M"]

            # Mac RAM & Image Reader (if applicable)
            imageSlot = ""
            if (
                system.name == "macintosh"
                and system.isOptSet("ramsize")
                and messModel in ["maciix", "maclc3"]
            ):
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
                    commandLine += ["-ramsize", str(ramSize) + "M"]
                    if messModel == "maciix":
                        imageSlot = "nba"
                    if system.isOptSet("imagereader"):
                        if system.config["imagereader"] == "disabled":
                            imageSlot = ""
                        else:
                            imageSlot = system.config["imagereader"]
                    if imageSlot != "":
                        commandLine += ["-" + imageSlot, "image"]

            if softList != "":
                # Software list ROM commands
                prepSoftwareList(
                    subdirSoftList,
                    softList,
                    softDir,
                    str(Path("/userdata/bios/mame/hash")),
                    romDirname,
                )
                if softList in subdirSoftList:
                    commandLine += [Path(romDirname).name]
                else:
                    commandLine += [romDrivername]
                commandLine += ["-rompath", f"{softDir};{Path('/userdata/bios/')!s}"]
                commandLine += ["-swpath", softDir]
                commandLine += ["-verbose"]
            else:
                # Alternate ROM type for systems with mutiple media (ie cassette & floppy)
                # Mac will auto change floppy 1 to 2 if a boot disk is enabled
                if system.name != "macintosh":
                    if system.isOptSet("altromtype"):
                        if (
                            system.config["altromtype"] == "flop1"
                            and messModel == "fmtmarty"
                        ):
                            commandLine += ["-flop"]
                        else:
                            commandLine += ["-" + system.config["altromtype"]]
                    elif system.name == "adam":
                        # add some logic based on the extension
                        rom_extension = Path(rom).suffix.lower()
                        if rom_extension == ".ddp":
                            commandLine += ["-cass1"]
                        elif rom_extension == ".dsk":
                            commandLine += ["-flop1"]
                        else:
                            commandLine += ["-cart1"]
                    elif system.name == "coco":
                        if romExt.casefold() == ".cas":
                            commandLine += ["-cass"]
                        elif romExt.casefold() == ".dsk":
                            commandLine += ["-flop1"]
                        else:
                            commandLine += ["-cart"]
                    # try to choose the right floppy for Apple2gs
                    elif system.name == "apple2gs":
                        rom_extension = Path(rom).suffix.lower()
                        if rom_extension == ".zip":
                            with ZipFile(rom, "r") as zip_file:
                                file_list = zip_file.namelist()
                                # assume only one file in zip
                                if len(file_list) == 1:
                                    filename = file_list[0]
                                    rom_extension = Path(filename).suffix.lower()
                        if rom_extension in [".2mg", ".2img", ".img", ".image"]:
                            commandLine += ["-flop3"]
                        else:
                            commandLine += ["-flop1"]
                    else:
                        commandLine += ["-" + messRomType[messMode]]
                elif system.isOptSet("bootdisk"):
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
                        commandLine += ["-flop2"]
                    elif system.isOptSet("altromtype"):
                        commandLine += ["-" + system.config["altromtype"]]
                    else:
                        commandLine += ["-" + messRomType[messMode]]
                elif system.isOptSet("altromtype"):
                    commandLine += ["-" + system.config["altromtype"]]
                else:
                    commandLine += ["-" + messRomType[messMode]]
                # Use the full filename for MESS non-softlist ROMs
                commandLine += [f'"{rom}"']
                commandLine += [
                    "-rompath",
                    f"{romDirname};{Path('/userdata/bios/')!s}",
                ]

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
                        bootDisk = f'"{Path("/userdata/bios") / (system.config["bootdisk"] + ".img")!s}"'
                    else:
                        bootType = "-hard"
                        bootDisk = f'"{Path("/userdata/bios") / (system.config["bootdisk"] + ".chd")!s}"'
                    commandLine += [bootType, bootDisk]

                # Create & add a blank disk if needed, insert into drive 2
                # or drive 1 if drive 2 is selected manually or FM Towns Marty.
                if (
                    system.isOptSet("addblankdisk")
                    and system.getOptBoolean("addblankdisk")
                    and system.name == "fmtowns"
                ):
                    blankDisk = Path("/usr/share/mame/blank.fmtowns")
                    targetFolder = Path("/userdata/saves/mame") / system.name
                    targetDisk = targetFolder / f"{Path(romBasename).stem}.fmtowns"
                    # Add elif statements here for other systems if enabled
                    if not targetFolder.exists():
                        targetFolder.mkdir(parents=True, exist_ok=True)
                    if not targetDisk.exists():
                        copy2(blankDisk, targetDisk)

                    # Add other single floppy systems to this if statement
                    if messModel == "fmtmarty":
                        commandLine += ["-flop", str(targetDisk)]
                    elif (
                        system.isOptSet("altromtype")
                        and system.config["altromtype"] == "flop2"
                    ):
                        commandLine += ["-flop1", str(targetDisk)]
                    else:
                        commandLine += ["-flop2", str(targetDisk)]

            # UI enable - for computer systems, the default sends all keys to the emulated system.
            # This will enable hotkeys, but some keys may pass through to MAME and not be usable in the emulated system.
            if not (
                system.isOptSet("enableui") and not system.getOptBoolean("enableui")
            ):
                commandLine += ["-ui_active"]

            # MESS config folder
            if system.getOptBoolean("customcfg"):
                cfgPath = (
                    Path("/userdata/system/configs")
                    / corePath
                    / messSysName[messMode]
                    / "custom/"
                )
            else:
                cfgPath = Path("/userdata/saves/mame/mame/cfg") / messSysName[messMode]
            if system.getOptBoolean("pergamecfg"):
                cfgPath = (
                    Path("/userdata/system/configs")
                    / corePath
                    / messSysName[messMode]
                    / romBasename
                )
            if not cfgPath.exists():
                cfgPath.mkdir(parents=True, exist_ok=True)
            commandLine += ["-cfg_directory", str(cfgPath)]

            # Autostart via ini file
            # Init variables, delete old ini if it exists, prepare ini path
            # lr-mame does NOT support multiple ini paths
            autoRunCmd = ""
            autoRunDelay = 0
            ini_path = Path("/userdata/saves/mame/mame/ini/")
            if not ini_path.exists():
                ini_path.mkdir(parents=True, exist_ok=True)
            batocera_ini_path = ini_path / "batocera.ini"
            if batocera_ini_path.exists():
                batocera_ini_path.unlink()
            # bbc has different boots for floppy & cassette, no special boot for carts
            if system.name == "bbc":
                if system.isOptSet("altromtype") or softList != "":
                    if (
                        system.isOptSet("altromtype")
                        and system.config["altromtype"] == "cass"
                    ) or softList[-4:] == "cass":
                        autoRunCmd = '*tape\\nchain""\\n'
                        autoRunDelay = 2
                    elif (
                        system.isOptSet("altromtype")
                        and system.config["altromtype"].startswith("flop")
                    ) or "flop" in softList:
                        autoRunCmd = "*cat\\n\\n\\n\\n*exec !boot\\n"
                        autoRunDelay = 3
                else:
                    autoRunCmd = "*cat\\n\\n\\n\\n*exec !boot\\n"
                    autoRunDelay = 3
            # fm7 boots floppies, needs cassette loading
            elif (
                system.name == "fm7"
                and (system.isOptSet("altromtype") or softList != "")
                and (
                    (
                        system.isOptSet("altromtype")
                        and system.config["altromtype"] == "cass"
                    )
                    or softList[-4:] == "cass"
                )
            ):
                autoRunCmd = "LOADM”“,,R\\n"
                autoRunDelay = 5
            elif system.name == "coco":
                romType = "cart"
                autoRunDelay = 2

                # if using software list, use "usage" for autoRunCmd (if provided)
                if softList != "":
                    softListFile = Path("/usr/bin/mame/hash") / f"{softList}.xml"
                    if softListFile.exists():
                        softwarelist = ET.parse(softListFile)
                        for software in softwarelist.findall("software"):
                            if (
                                software.attrib != {}
                                and software.get("name") == romDrivername
                            ):
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
                        romType = "cass"
                        if romDrivername.casefold().endswith(".bas"):
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
                        romType = "flop"
                        if romDrivername.casefold().endswith(".bas"):
                            autoRunCmd = f'RUN "{romDrivername}"\\n'
                        else:
                            autoRunCmd = f'LOADM "{romDrivername}":EXEC\\n'

                # check for a user override
                autoRunFile = (
                    Path("system/configs/mame/autoload")
                    / f"{system.name}_{romType}_autoload.csv"
                )
                if autoRunFile.exists():
                    with Path(str(autoRunFile)).open() as openARFile:
                        autoRunList = reader(openARFile, delimiter=";", quotechar="'")
                        for row in autoRunList:
                            if (
                                row
                                and not row[0].startswith("#")
                                and row[0].casefold() == romDrivername.casefold()
                            ):
                                autoRunCmd = row[1] + "\\n"
            else:
                # Check for an override file, otherwise use generic (if it exists)
                autoRunCmd = messAutoRun[messMode]
                autoRunFile = (
                    Path("/usr/share/reglinux/configgen/data/mame")
                    / f"{softList}_autoload.csv"
                )
                if autoRunFile.exists():
                    with Path(str(autoRunFile)).open() as openARFile:
                        autoRunList = reader(openARFile, delimiter=";", quotechar="'")
                        for row in autoRunList:
                            if row[0].casefold() == Path(romBasename).stem.casefold():
                                autoRunCmd = row[1] + "\\n"
                                autoRunDelay = 3
            commandLine += ["-inipath", str(Path("/userdata/saves/mame/mame/ini/"))]
            if autoRunCmd is not None:
                if autoRunCmd.startswith("'"):
                    autoRunCmd.replace("'", "")
                with Path(str(batocera_ini_path)).open("w") as iniFile:
                    iniFile.write("autoboot_command          " + autoRunCmd + "\n")
                    iniFile.write("autoboot_delay            " + str(autoRunDelay))
            # Create & add a blank disk if needed, insert into drive 2
            # or drive 1 if drive 2 is selected manually.
            blank_disk_path = (
                Path("/userdata/saves/lr-mess")
                / system.name
                / f"{Path(romBasename).stem}.dsk"
            )
            if system.isOptSet("addblankdisk") and system.getOptBoolean("addblankdisk"):
                if not blank_disk_path.exists():
                    blank_disk_path.parent.mkdir(parents=True, exist_ok=True)
                    copy2(
                        Path("/usr/share/mame/blank.dsk"),
                        blank_disk_path,
                    )
                if (
                    system.isOptSet("altromtype")
                    and system.config["altromtype"] == "flop2"
                ):
                    commandLine += [
                        "-flop1",
                        str(blank_disk_path),
                    ]
                else:
                    commandLine += [
                        "-flop2",
                        str(blank_disk_path),
                    ]

    # Lightgun reload option
    if system.isOptSet("offscreenreload") and system.getOptBoolean("offscreenreload"):
        commandLine += ["-offscreen_reload"]

    # Art paths - lr-mame displays artwork in the game area and not in the bezel area, so using regular MAME artwork + shaders is not recommended.
    # By default, will ignore standalone MAME's art paths.
    if system.config["core"] != "same_cdi":
        if not (
            system.isOptSet("sharemameart") and not system.getOptBoolean("sharemameart")
        ):
            artPath = "/var/run/mame_artwork/;/usr/bin/mame/artwork/;/userdata/bios/lr-mame/artwork/;/userdata/bios/mame/artwork/;/userdata/decorations/"
        else:
            artPath = "/var/run/mame_artwork/;/usr/bin/mame/artwork/;/userdata/bios/lr-mame/artwork/"
        if system.name != "ti99":
            commandLine += ["-artpath", artPath]

    # Artwork crop - default to On for lr-mame
    # Exceptions for PDP-1 (status lights) and VGM Player (indicators)
    if not system.isOptSet("artworkcrop"):
        if system.name not in ["pdp1", "ti99"]:
            commandLine += ["-artwork_crop"]
    elif system.getOptBoolean("artworkcrop"):
        commandLine += ["-artwork_crop"]

    # Share plugins & samples with standalone MAME (except TI99)
    if system.name != "ti99":
        commandLine += [
            "-pluginspath",
            f"{Path('/usr/bin/mame/plugins/')!s};{Path('/userdata/saves/mame/plugins')!s}",
        ]
        commandLine += ["-homepath", str(Path("/userdata/saves/mame/plugins/"))]
        commandLine += ["-samplepath", str(Path("/userdata/bios/mame/samples/"))]
    plugins_path = Path("/userdata/saves/mame/plugins/")
    if not plugins_path.exists():
        plugins_path.mkdir(parents=True, exist_ok=True)
    samples_path = Path("/userdata/bios/mame/samples/")
    if not samples_path.exists():
        samples_path.mkdir(parents=True, exist_ok=True)

    # Delete old cmd files & prepare path
    cmdPath = Path("/var/run/cmdfiles/")
    if not cmdPath.exists():
        cmdPath.mkdir(parents=True, exist_ok=True)
    cmdFileList = listdir(cmdPath)
    for file in cmdFileList:
        if file.endswith(".cmd"):
            Path(str(cmdPath / file)).unlink()

    # Write command line file
    cmdFilename = cmdPath / f"{romDrivername}.cmd"
    Path(str(cmdFilename)).write_text(" ".join(commandLine))

    # Call Controller Config
    if messMode == -1:
        generateMAMEPadConfig(
            str(cfgPath),
            playersControllers,
            system,
            "",
            romBasename,
            specialController,
            guns,
        )
    else:
        generateMAMEPadConfig(
            str(cfgPath),
            playersControllers,
            system,
            messModel,
            romBasename,
            specialController,
            guns,
        )

    return commandLine


def prepSoftwareList(
    subdirSoftList: list[str],
    softList: str,
    softDir: str,
    hashDir: str,
    romDirname: str,
) -> None:
    softDir_path = Path(softDir)
    if not softDir_path.exists():
        softDir_path.mkdir(parents=True, exist_ok=True)
    # Check for/remove existing symlinks, remove hashfile folder
    for fileName in listdir(softDir):
        checkFile = Path(softDir) / fileName
        if checkFile.is_symlink():
            checkFile.unlink()
        if checkFile.is_dir():
            rmtree(checkFile)
    # Prepare hashfile path
    hashDir_path = Path(hashDir)
    if not hashDir_path.exists():
        hashDir_path.mkdir(parents=True, exist_ok=True)
    # Remove existing xml files
    hashFiles = listdir(hashDir)
    for file in hashFiles:
        if file.endswith(".xml"):
            Path(str(Path(hashDir) / file)).unlink()
    # Copy hashfile
    copy2(
        str(Path("/usr/bin/mame/hash") / f"{softList}.xml"),
        str(Path(hashDir) / f"{softList}.xml"),
    )
    # Link ROM's parent folder if needed, ROM's folder otherwise
    if softList in subdirSoftList:
        romPath = Path(romDirname)
        Path(str(Path(softDir) / softList)).symlink_to(str(romPath.parents[0]), target_is_directory=True)
    else:
        Path(str(Path(softDir) / softList)).symlink_to(romDirname, target_is_directory=True)


def getMameControlScheme(system: Any, romBasename: str) -> Any:
    # Game list files
    mameCapcom = str(Path("/usr/share/reglinux/configgen/data/mame/mameCapcom.txt"))
    mameKInstinct = str(
        Path("/usr/share/reglinux/configgen/data/mame/mameKInstinct.txt"),
    )
    mameMKombat = str(Path("/usr/share/reglinux/configgen/data/mame/mameMKombat.txt"))
    mameNeogeo = str(Path("/usr/share/reglinux/configgen/data/mame/mameNeogeo.txt"))
    mameTwinstick = str(
        Path("/usr/share/reglinux/configgen/data/mame/mameTwinstick.txt"),
    )
    mameRotatedstick = str(
        Path("/usr/share/reglinux/configgen/data/mame/mameRotatedstick.txt"),
    )

    # Controls for games with 5-6 buttons or other unusual controls
    if system.isOptSet("altlayout"):
        controllerType = system.config["altlayout"]  # Option was manually selected
    else:
        controllerType = "auto"

    if controllerType in ["default", "neomini", "neocd", "twinstick", "qbert"]:
        return controllerType
    try:
        with Path(mameCapcom).open() as f:
            capcomList = set(f.read().split())
        with Path(mameMKombat).open() as f:
            mkList = set(f.read().split())
        with Path(mameKInstinct).open() as f:
            kiList = set(f.read().split())
        with Path(mameNeogeo).open() as f:
            neogeoList = set(f.read().split())
        with Path(mameTwinstick).open() as f:
            twinstickList = set(f.read().split())
        with Path(mameRotatedstick).open() as f:
            qbertList = set(f.read().split())
    except OSError as e:
        eslog.error(f"Error reading MAME list files: {e}")
        # Initialize empty sets to avoid breaking the process
        capcomList = set()
        mkList = set()
        kiList = set()
        neogeoList = set()
        twinstickList = set()
        qbertList = set()

    romName = Path(romBasename).stem
    if romName in capcomList:
        if controllerType in ["auto", "snes"]:
            return "sfsnes"
        if controllerType == "megadrive":
            return "megadrive"
        if controllerType == "fightstick":
            return "sfstick"
    elif romName in mkList:
        if controllerType in ["auto", "snes"]:
            return "mksnes"
        if controllerType == "megadrive":
            return "mkmegadrive"
        if controllerType == "fightstick":
            return "mkstick"
    elif romName in kiList:
        if controllerType in ["auto", "snes"]:
            return "kisnes"
        if controllerType == "megadrive":
            return "megadrive"
        if controllerType == "fightstick":
            return "sfstick"
    elif romName in neogeoList:
        return "neomini"
    elif romName in twinstickList:
        return "twinstick"
    elif romName in qbertList:
        return "qbert"
    elif controllerType == "fightstick":
        return "fightstick"

    return "default"


def generateMAMEPadConfig(
    cfgPath: str,
    playersControllers: Any,
    system: Any,
    messSysName: str,
    romBasename: str,
    specialController: str,
    guns: Any,
) -> None:
    # config file
    config = minidom.Document()
    configFile = Path(cfgPath) / "default.cfg"
    if configFile.exists():
        try:
            config = minidom.parse(str(configFile))
        except xml.parsers.expat.ExpatError as e:
            eslog.warning(
                f"Invalid XML in MAME config file {configFile}: {e}. Reinitializing file.",
            )
            config = minidom.Document()  # Reinitialize on parse error
        except FileNotFoundError:
            eslog.warning(f"MAME config file not found: {configFile}")
            config = minidom.Document()  # Reinitialize if file not found
        except Exception as e:
            eslog.warning(
                f"Error parsing MAME config file {configFile}: {e}. Reinitializing file.",
            )
            config = minidom.Document()  # Reinitialize on any error

    if system.isOptSet("customcfg"):
        customCfg = system.getOptBoolean("customcfg")
    else:
        customCfg = False
    # Don't overwrite if using custom configs
    overwriteMAME = not (configFile.exists() and customCfg)

    # Get controller scheme
    altButtons = getMameControlScheme(system, romBasename)

    # Load standard controls from csv
    controlFile = "/usr/share/reglinux/configgen/data/mame/mameControls.csv"
    with Path(controlFile).open() as openFile:
        controlDict = {}
        controlList = reader(openFile)
        for row in controlList:
            if row[0] not in controlDict:
                controlDict[row[0]] = {}
            controlDict[row[0]][row[1]] = row[2]

    # Common controls
    mappings = {}
    for controlDef in controlDict["default"]:
        mappings[controlDef] = controlDict["default"][controlDef]

    # Buttons that change based on game/setting
    if altButtons in controlDict:
        for controlDef in controlDict[altButtons]:
            mappings.update({controlDef: controlDict[altButtons][controlDef]})

    xml_mameconfig = getRoot(config, "mameconfig")
    xml_mameconfig.setAttribute("version", "10")
    xml_system = getSection(config, xml_mameconfig, "system")
    xml_system.setAttribute("name", "default")

    removeSection(config, xml_system, "input")
    xml_input = config.createElement("input")
    xml_system.appendChild(xml_input)

    messControlDict = {}
    if messSysName in ["bbcb", "bbcm", "bbcm512", "bbcmc"]:
        if specialController == "none":
            useControls = "bbc"
        else:
            useControls = f"bbc-{specialController}"
    elif messSysName in ["apple2p", "apple2e", "apple2ee"]:
        if specialController == "none":
            useControls = "apple2"
        else:
            useControls = f"apple2-{specialController}"
    else:
        useControls = messSysName

    # Open or create alternate config file for systems with special controllers/settings
    # If the system/game is set to per game config, don't try to open/reset an existing file, only write if it's blank or going to the shared cfg folder
    specialControlList = [
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

    # Initialize config_alt and xml_input_alt outside the conditional block
    config_alt = minidom.Document()
    configFile_alt = Path(cfgPath) / f"{messSysName}.cfg"
    xml_mameconfig_alt = getRoot(config_alt, "mameconfig")
    xml_mameconfig_alt.setAttribute("version", "10")
    xml_system_alt = getSection(config_alt, xml_mameconfig_alt, "system")
    xml_system_alt.setAttribute("name", messSysName)
    xml_input_alt = config_alt.createElement("input")
    overwriteSystem = True
    if messSysName in specialControlList:
        # Load mess controls from csv
        messControlFile = Path(
            "/usr/share/reglinux/configgen/data/mame/messControls.csv",
        )
        with Path(str(messControlFile)).open() as openMessFile:
            controlList = reader(openMessFile, delimiter=";")
            for row in controlList:
                if row[0] not in messControlDict:
                    messControlDict[row[0]] = {}
                messControlDict[row[0]][row[1]] = {}
                currentEntry = messControlDict[row[0]][row[1]]
                currentEntry["type"] = row[2]
                currentEntry["player"] = int(row[3])
                currentEntry["tag"] = row[4]
                currentEntry["key"] = row[5]
                if currentEntry["type"] in ["special", "main"]:
                    currentEntry["mapping"] = row[6]
                    currentEntry["useMapping"] = row[7]
                    currentEntry["reversed"] = row[8]
                    currentEntry["mask"] = row[9]
                    currentEntry["default"] = row[10]
                elif currentEntry["type"] == "analog":
                    currentEntry["incMapping"] = row[6]
                    currentEntry["decMapping"] = row[7]
                    currentEntry["useMapping1"] = row[8]
                    currentEntry["useMapping2"] = row[9]
                    currentEntry["reversed"] = row[10]
                    currentEntry["mask"] = row[11]
                    currentEntry["default"] = row[12]
                    currentEntry["delta"] = row[13]
                    currentEntry["axis"] = row[14]
                if currentEntry["type"] == "combo":
                    currentEntry["kbMapping"] = row[6]
                    currentEntry["mapping"] = row[7]
                    currentEntry["useMapping"] = row[8]
                    currentEntry["reversed"] = row[9]
                    currentEntry["mask"] = row[10]
                    currentEntry["default"] = row[11]
                if currentEntry["reversed"] == "False":
                    currentEntry["reversed"] = False
                else:
                    currentEntry["reversed"] = True

        config_alt = minidom.Document()
        if configFile_alt.exists():
            try:
                config_alt = minidom.parse(str(configFile_alt))
            except xml.parsers.expat.ExpatError as e:
                eslog.warning(
                    f"Invalid XML in MAME alt config file {configFile_alt}: {e}. Reinitializing file.",
                )
                # reinit the file
            except FileNotFoundError:
                eslog.warning(f"MAME alt config file not found: {configFile_alt}")
                # reinit the file
            except Exception as e:
                eslog.warning(
                    f"Error parsing MAME alt config file {configFile_alt}: {e}. Reinitializing file.",
                )
                # reinit the file

        perGameCfg = system.getOptBoolean("pergamecfg")
        if configFile_alt.exists() and (customCfg or perGameCfg):
            overwriteSystem = False
        else:
            overwriteSystem = True

        xml_mameconfig_alt = getRoot(config_alt, "mameconfig")
        xml_mameconfig_alt.setAttribute("version", "10")
        xml_system_alt = getSection(config_alt, xml_mameconfig_alt, "system")
        xml_system_alt.setAttribute("name", messSysName)

        removeSection(config_alt, xml_system_alt, "input")
        xml_input_alt = config_alt.createElement("input")
        xml_system_alt.appendChild(xml_input_alt)

        # Hide the LCD display on CD-i
        if useControls == "cdimono1":
            removeSection(config_alt, xml_system_alt, "video")
            xml_video_alt = config_alt.createElement("video")
            xml_system_alt.appendChild(xml_video_alt)

            xml_screencfg_alt = config_alt.createElement("target")
            xml_screencfg_alt.setAttribute("index", "0")
            xml_screencfg_alt.setAttribute("view", "Main Screen Standard (4:3)")
            xml_video_alt.appendChild(xml_screencfg_alt)

        # If using BBC keyboard controls, enable keyboard to gamepad
        if useControls == "bbc":
            xml_kbenable_alt = config_alt.createElement("keyboard")
            xml_kbenable_alt.setAttribute("tag", ":")
            xml_kbenable_alt.setAttribute("enabled", "1")
            xml_input_alt.appendChild(xml_kbenable_alt)

    # Don't configure pads if guns are present and "use_guns" is on
    if (
        system.isOptSet("use_guns")
        and system.getOptBoolean("use_guns")
        and len(guns) > 0
    ):
        return

    # Fill in controls on cfg files
    nplayer = 1
    for _, pad in sorted(playersControllers.items()):
        mappings_use = mappings
        if "joystick1up" not in pad.inputs:
            mappings_use["JOYSTICK_UP"] = "up"
            mappings_use["JOYSTICK_DOWN"] = "down"
            mappings_use["JOYSTICK_LEFT"] = "left"
            mappings_use["JOYSTICK_RIGHT"] = "right"

        for mapping in mappings_use:
            if mappings_use[mapping] in pad.inputs:
                if mapping in ["START", "COIN"]:
                    xml_input.appendChild(
                        generateSpecialPortElement(
                            pad,
                            config,
                            "standard",
                            nplayer,
                            pad.index,
                            mapping + str(nplayer),
                            mappings_use[mapping],
                            retroPad[mappings_use[mapping]],
                            False,
                            "",
                            "",
                        ),
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
                            retroPad[mappings_use[mapping]],
                            False,
                            altButtons,
                        ),
                    )
            else:
                rmapping = reverseMapping(mappings_use[mapping])
                if rmapping in retroPad:
                    xml_input.appendChild(
                        generatePortElement(
                            pad,
                            config,
                            nplayer,
                            pad.index,
                            mapping,
                            mappings_use[mapping],
                            retroPad[rmapping],
                            True,
                            altButtons,
                        ),
                    )

        # UI Mappings
        if nplayer == 1:
            xml_input.appendChild(
                generateComboPortElement(
                    pad,
                    config,
                    "standard",
                    pad.index,
                    "UI_DOWN",
                    "DOWN",
                    mappings_use["JOYSTICK_DOWN"],
                    retroPad[mappings_use["JOYSTICK_DOWN"]],
                    False,
                    "",
                    "",
                ),
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
                    retroPad[mappings_use["JOYSTICK_LEFT"]],
                    False,
                    "",
                    "",
                ),
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
                    retroPad[mappings_use["JOYSTICK_UP"]],
                    False,
                    "",
                    "",
                ),
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
                    retroPad[mappings_use["JOYSTICK_RIGHT"]],
                    False,
                    "",
                    "",
                ),
            )  # Right
            xml_input.appendChild(
                generateComboPortElement(
                    pad,
                    config,
                    "standard",
                    pad.index,
                    "UI_SELECT",
                    "ENTER",
                    "a",
                    retroPad["a"],
                    False,
                    "",
                    "",
                ),
            )  # Select

        # Handle special controls only if we're using a system that needs them
        if useControls in messControlDict and messSysName in specialControlList:
            for controlDef in messControlDict[useControls]:
                thisControl = messControlDict[useControls][controlDef]
                if nplayer == thisControl["player"]:
                    if thisControl["type"] == "special":
                        xml_input_alt.appendChild(
                            generateSpecialPortElement(
                                pad,
                                config_alt,
                                thisControl["tag"],
                                nplayer,
                                pad.index,
                                thisControl["key"],
                                thisControl["mapping"],
                                retroPad[mappings_use[thisControl["useMapping"]]],
                                thisControl["reversed"],
                                thisControl["mask"],
                                thisControl["default"],
                            ),
                        )
                    elif thisControl["type"] == "main":
                        xml_input.appendChild(
                            generateSpecialPortElement(
                                pad,
                                config_alt,
                                thisControl["tag"],
                                nplayer,
                                pad.index,
                                thisControl["key"],
                                thisControl["mapping"],
                                retroPad[mappings_use[thisControl["useMapping"]]],
                                thisControl["reversed"],
                                thisControl["mask"],
                                thisControl["default"],
                            ),
                        )
                    elif thisControl["type"] == "analog":
                        xml_input_alt.appendChild(
                            generateAnalogPortElement(
                                pad,
                                config_alt,
                                thisControl["tag"],
                                nplayer,
                                pad.index,
                                thisControl["key"],
                                mappings_use[thisControl["incMapping"]],
                                mappings_use[thisControl["decMapping"]],
                                retroPad[mappings_use[thisControl["useMapping1"]]],
                                retroPad[mappings_use[thisControl["useMapping2"]]],
                                thisControl["reversed"],
                                thisControl["mask"],
                                thisControl["default"],
                                thisControl["delta"],
                                thisControl["axis"],
                            ),
                        )
                    elif thisControl["type"] == "combo":
                        xml_input_alt.appendChild(
                            generateComboPortElement(
                                pad,
                                config_alt,
                                thisControl["tag"],
                                pad.index,
                                thisControl["key"],
                                thisControl["kbMapping"],
                                thisControl["mapping"],
                                retroPad[mappings_use[thisControl["useMapping"]]],
                                thisControl["reversed"],
                                thisControl["mask"],
                                thisControl["default"],
                            ),
                        )

        nplayer = nplayer + 1

    # save the config file
    # mameXml = open(configFile, "w")
    # TODO: python 3 - workawround to encode files in utf-8
    if overwriteMAME:
        with Path(str(configFile)).open("w", encoding="utf-8") as mameXml:
            dom_string = linesep.join(
                [s for s in config.toprettyxml().splitlines() if s.strip()],
            )  # remove ugly empty lines while minicom adds them...
            mameXml.write(dom_string)

    # Write alt config (if used, custom config is turned off or file doesn't exist yet)
    if messSysName in specialControlList and overwriteSystem:
        with Path(str(configFile_alt)).open("w", encoding="utf-8") as mameXml_alt:
            dom_string_alt = linesep.join(
                [s for s in config_alt.toprettyxml().splitlines() if s.strip()],
            )  # remove ugly empty lines while minicom adds them...
            mameXml_alt.write(dom_string_alt)


def reverseMapping(key: str) -> str:
    if key == "joystick1down":
        return "joystick1up"
    if key == "joystick1right":
        return "joystick1left"
    if key == "joystick2down":
        return "joystick2up"
    if key == "joystick2right":
        return "joystick2left"
    return key  # Return the original key if no match is found


def generatePortElement(
    pad: Any,
    config: Any,
    nplayer: int,
    padindex: int,
    mapping: str,
    key: str,
    input_param: str,
    reversed_param: Any,
    altButtons: Any,
) -> Any:
    # Generic input
    xml_port = config.createElement("port")
    xml_port.setAttribute("type", f"P{nplayer}_{mapping}")
    xml_newseq = config.createElement("newseq")
    xml_newseq.setAttribute("type", "standard")
    xml_port.appendChild(xml_newseq)
    value = config.createTextNode(
        input2definition(pad, key, input_param, padindex, reversed_param, altButtons),
    )
    xml_newseq.appendChild(value)
    return xml_port


def generateSpecialPortElement(
    pad: Any,
    config: Any,
    tag: str,
    nplayer: int,
    padindex: int,
    mapping: str,
    key: str,
    input_param: str,
    reversed_param: Any,
    mask: str,
    default: Any,
) -> Any:
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
        input2definition(pad, key, input_param, padindex, reversed_param, 0),
    )
    xml_newseq.appendChild(value)
    return xml_port


def generateComboPortElement(
    pad: Any,
    config: Any,
    tag: str,
    padindex: int,
    mapping: str,
    kbkey: str,
    key: str,
    input_param: str,
    reversed_param: Any,
    mask: str,
    default: Any,
) -> Any:
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
        + input2definition(pad, key, input_param, padindex, reversed_param, 0),
    )
    xml_newseq.appendChild(value)
    return xml_port


def generateAnalogPortElement(
    pad: Any,
    config: Any,
    tag: str,
    nplayer: int,
    padindex: int,
    mapping: str,
    inckey: str,
    deckey: str,
    mappedinput: str,
    mappedinput2: str,
    reversed_param: Any,
    mask: str,
    default: Any,
    delta: Any,
    axis: str = "",
) -> Any:
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
        input2definition(pad, inckey, mappedinput, padindex, reversed_param, 0, True),
    )
    xml_newseq_inc.appendChild(incvalue)
    xml_newseq_dec = config.createElement("newseq")
    xml_port.appendChild(xml_newseq_dec)
    xml_newseq_dec.setAttribute("type", "decrement")
    decvalue = config.createTextNode(
        input2definition(pad, deckey, mappedinput2, padindex, reversed_param, 0, True),
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
    input_param: str,
    joycode: Any,
    reversed_param: Any,
    altButtons: Any,
    ignoreAxis: bool = False,
) -> str:
    if (
        input_param.find("BUTTON") != -1
        or input_param.find("HAT") != -1
        or input_param == "START"
        or input_param == "SELECT"
    ):
        input_param = (
            input_param.replace("{0}", joycode) if "{0}" in input_param else input_param
        )
        return f"JOYCODE_{joycode}_{input_param}"
    if input_param.find("AXIS") != -1:
        if altButtons == "qbert":  # Q*Bert Joystick
            if key == "joystick1up" or key == "up":
                return f"JOYCODE_{joycode}_{retroPad['joystick1up']}_{joycode}_{retroPad['joystick1right']} OR \
                    JOYCODE_{joycode}_{retroPad['up'].replace('{0}', joycode)} JOYCODE_{joycode}_{retroPad['right'].replace('{0}', joycode)}"
            if key == "joystick1down" or key == "down":
                return f"JOYCODE_{joycode}_{retroPad['joystick1down']} JOYCODE_{joycode}_{retroPad['joystick1left']} OR \
                    JOYCODE_{joycode}_{retroPad['down'].replace('{0}', joycode)} JOYCODE_{joycode}_{retroPad['left'].replace('{0}', joycode)}"
            if key == "joystick1left" or key == "left":
                return f"JOYCODE_{joycode}_{retroPad['joystick1left']} JOYCODE_{joycode}_{retroPad['joystick1up']} OR \
                    JOYCODE_{joycode}_{retroPad['left'].replace('{0}', joycode)} JOYCODE_{joycode}_{retroPad['up'].replace('{0}', joycode)}"
            if key == "joystick1right" or key == "right":
                return f"JOYCODE_{joycode}_{retroPad['joystick1right']} JOYCODE_{joycode}_{retroPad['joystick1down']} OR \
                    JOYCODE_{joycode}_{retroPad['right'].replace('{0}', joycode)} JOYCODE_{joycode}_{retroPad['down'].replace('{0}', joycode)}"
            return f"JOYCODE_{joycode}_{input}"
        if ignoreAxis:
            if key == "joystick1up" or key == "up":
                return f"JOYCODE_{joycode}_{retroPad['up'].replace('{0}', joycode)}"
            if key == "joystick1down" or key == "down":
                return f"JOYCODE_{joycode}_{retroPad['down'].replace('{0}', joycode)}"
            if key == "joystick1left" or key == "left":
                return f"JOYCODE_{joycode}_{retroPad['left'].replace('{0}', joycode)}"
            if key == "joystick1right" or key == "right":
                return f"JOYCODE_{joycode}_{retroPad['right'].replace('{0}', joycode)}"
            return f"JOYCODE_{joycode}_{input}"
        if key == "joystick1up" or key == "up":
            return f"JOYCODE_{joycode}_{retroPad[key]} OR JOYCODE_{joycode}_{retroPad['up'].replace('{0}', joycode)}"
        if key == "joystick1down" or key == "down":
            return f"JOYCODE_{joycode}_{retroPad[key]} OR JOYCODE_{joycode}_{retroPad['down'].replace('{0}', joycode)}"
        if key == "joystick1left" or key == "left":
            return f"JOYCODE_{joycode}_{retroPad[key]} OR JOYCODE_{joycode}_{retroPad['left'].replace('{0}', joycode)}"
        if key == "joystick1right" or key == "right":
            return f"JOYCODE_{joycode}_{retroPad[key]} OR JOYCODE_{joycode}_{retroPad['right'].replace('{0}', joycode)}"
        if key == "joystick2up":
            return f"JOYCODE_{joycode}_{retroPad[key]} OR JOYCODE_{joycode}_{retroPad['x']}"
        if key == "joystick2down":
            return f"JOYCODE_{joycode}_{retroPad[key]} OR JOYCODE_{joycode}_{retroPad['b']}"
        if key == "joystick2left":
            return f"JOYCODE_{joycode}_{retroPad[key]} OR JOYCODE_{joycode}_{retroPad['y']}"
        if key == "joystick2right":
            return f"JOYCODE_{joycode}_{retroPad[key]} OR JOYCODE_{joycode}_{retroPad['a']}"
        return f"JOYCODE_{joycode}_{input}"
    return "unknown"


def getRoot(config: Any, name: str) -> Any:
    xml_section = config.getElementsByTagName(name)

    if len(xml_section) == 0:
        xml_section = config.createElement(name)
        config.appendChild(xml_section)
    else:
        xml_section = xml_section[0]

    return xml_section


def getSection(config: Any, xml_root: Any, name: str) -> Any:
    xml_section = xml_root.getElementsByTagName(name)

    if len(xml_section) == 0:
        xml_section = config.createElement(name)
        xml_root.appendChild(xml_section)
    else:
        xml_section = xml_section[0]

    return xml_section


def removeSection(config: Any, xml_root: Any, name: str) -> None:
    xml_section = xml_root.getElementsByTagName(name)

    for i in range(len(xml_section)):
        old = xml_root.removeChild(xml_section[i])
        old.unlink()
