from generators.Generator import Generator
from Command import Command
from typing import Optional, Tuple
from filecmp import cmp
from shutil import copyfile, copytree, copy2
from os import path, walk, mkdir, listdir
from ffmpeg import probe
from controllers import generate_sdl_controller_config, gunsBordersSizeName
from systemFiles import CONF, ROMS, SAVES
from utils.logger import get_logger

DAPHNE_ROM_DIR = ROMS + "/daphne"
SINGE_ROM_DIR = ROMS + "/singe"
HYPSEUS_DATA_DIR = CONF + "/hypseus-singe"
HYPSEUS_CONFIG_FILE_PATH = "/hypinput.ini"
HYPSEUS_CONFIG_PATH = HYPSEUS_DATA_DIR + HYPSEUS_CONFIG_FILE_PATH
HYPSEUS_CONFIG_GAMEPAD_PATH = "/usr/share/hypseus-singe/hypinput_gamepad.ini"
HYPSEUS_SAVES_DIR = SAVES + "/hypseus"
HYPSEUS_BIN_PATH = "/usr/bin/hypseus"


eslog = get_logger(__name__)


class HypseusSingeGenerator(Generator):
    @staticmethod
    def find_m2v_from_txt(txt_file):
        with open(txt_file, "r") as file:
            for line in file:
                parts = line.strip().split()
                if parts:
                    filename = parts[-1]
                    if filename.endswith(".m2v"):
                        return filename
        return None

    @staticmethod
    def find_file(start_path, filename):
        if path.exists(path.join(start_path, filename)):
            return path.join(start_path, filename)

        for root, dirs, files in walk(start_path):
            if filename in files:
                eslog.debug(
                    "Found m2v file in path - {}".format(path.join(root, filename))
                )
                return path.join(root, filename)

        return None

    @staticmethod
    def get_resolution(video_path):
        try:
            # Try to get video information
            probe_video = probe(video_path)
            if not probe_video or "streams" not in probe_video:
                eslog.debug(
                    f"Could not parse the video file: {video_path}"
                )
                return 0, 0

            # Find the video stream
            video_stream = next(
                (
                    stream
                    for stream in probe_video["streams"]
                    if stream.get("codec_type") == "video"
                ),
                None,
            )
            if not video_stream:
                eslog.debug(f"No video stream found in: {video_path}")
                return 0, 0

            # Get width and height
            width = int(video_stream.get("width", 0))
            height = int(video_stream.get("height", 0))

            # Handle aspect ratio if available
            display_aspect_ratio = video_stream.get("display_aspect_ratio")
            if display_aspect_ratio and ":" in display_aspect_ratio:
                try:
                    sar_num, sar_den = display_aspect_ratio.split(":")
                    sar_num = int(sar_num) if sar_num else 0
                    sar_den = int(sar_den) if sar_den else 0
                    if sar_num != 0 and sar_den != 0:
                        ratio = sar_num / sar_den
                        width = int(height * ratio)
                except (ValueError, ZeroDivisionError) as e:
                    eslog.debug(f"Error processing aspect ratio: {e}")

            return width, height

        except Exception as e:
            eslog.error(f"Error getting video resolution: {e}")
            return 0, 0

    # Main entry of the module
    def generate(
        self, system, rom, playersControllers, metadata, guns, wheels, gameResolution
    ):
        bezel_to_rom = {
            "ace": ["ace", "ace_a", "ace_a2", "ace91", "ace91_euro", "aceeuro"],
            "astron": ["astron", "astronp"],
            "badlands": ["badlands", "badlandsp"],
            "bega": ["bega", "begar1"],
            "cliffhanger": ["cliffhanger", "cliff", "cliffalt", "cliffalt2"],
            "cobra": ["cobra", "cobraab", "cobraconv", "cobram3"],
            "conan": ["conan", "future_boy"],
            "chantze_hd": ["chantze_hd", "triad_hd", "triadstone"],
            "crimepatrol": ["crimepatrol", "crimepatrol-hd", "cp_hd"],
            "dle": ["dle", "dle_alt", "dle11", "dle21"],
            "dragon": ["dragon", "dragon_trainer"],
            "drugwars": ["drugwars", "drugwars-hd", "cp2dw_hd"],
            "daitarn": ["daitarn", "daitarn_3"],
            "fire_and_ice": ["fire_and_ice", "fire_and_ice_v2"],
            "galaxy": ["galaxy", "galaxyp"],
            "lair": [
                "lair",
                "lair_a",
                "lair_b",
                "lair_c",
                "lair_d",
                "lair_d2",
                "lair_e",
                "lair_f",
                "lair_ita",
                "lair_n1",
                "lair_x",
                "laireuro",
            ],
            "lbh": ["lbh", "lbh-hd", "lbh_hd"],
            "maddog": ["maddog", "maddog-hd", "maddog_hd"],
            "maddog2": ["maddog2", "maddog2-hd", "maddog2_hd"],
            "jack": ["jack", "samurai_jack"],
            "johnnyrock": ["johnnyrock", "johnnyrock-hd", "johnnyrocknoir", "wsjr_hd"],
            "pussinboots": ["pussinboots", "puss_in_boots"],
            "spacepirates": ["spacepirates", "spacepirates-hd", "space_pirates_hd"],
        }

        def find_bezel(rom_name):
            for bezel, rom_names in bezel_to_rom.items():
                if rom_name in rom_names:
                    return bezel
            return None

        if not path.isdir(HYPSEUS_DATA_DIR):
            mkdir(HYPSEUS_DATA_DIR)
        if not path.exists(HYPSEUS_CONFIG_PATH) or not cmp(
            HYPSEUS_CONFIG_GAMEPAD_PATH, HYPSEUS_CONFIG_PATH
        ):
            copyfile(HYPSEUS_CONFIG_GAMEPAD_PATH, HYPSEUS_CONFIG_PATH)

        # create a custom ini
        if not path.exists(HYPSEUS_DATA_DIR + "/custom.ini"):
            copyfile(HYPSEUS_CONFIG_PATH, HYPSEUS_DATA_DIR + "/custom.ini")

        # copy required resources to userdata config folder as needed
        def copy_resources(source_dir, destination_dir):
            if not path.exists(destination_dir):
                copytree(source_dir, destination_dir)
            else:
                for item in listdir(source_dir):
                    source_item = path.join(source_dir, item)
                    destination_item = path.join(destination_dir, item)
                    if path.isfile(source_item):
                        if not path.exists(destination_item) or path.getmtime(
                            source_item
                        ) > path.getmtime(destination_item):
                            copy2(source_item, destination_item)
                    elif path.isdir(source_item):
                        copy_resources(source_item, destination_item)

        directories = [
            {
                "source": "/usr/share/hypseus-singe/pics",
                "destination": HYPSEUS_DATA_DIR + "/pics",
            },
            {
                "source": "/usr/share/hypseus-singe/sound",
                "destination": HYPSEUS_DATA_DIR + "/sound",
            },
            {
                "source": "/usr/share/hypseus-singe/fonts",
                "destination": HYPSEUS_DATA_DIR + "/fonts",
            },
            {
                "source": "/usr/share/hypseus-singe/bezels",
                "destination": HYPSEUS_DATA_DIR + "/bezels",
            },
        ]

        # Copy/update directories
        for directory in directories:
            copy_resources(directory["source"], directory["destination"])

        # extension used .daphne and the file to start the game is in the folder .daphne with the extension .txt
        romName = path.splitext(path.basename(rom))[0]
        frameFile = rom + "/" + romName + ".txt"
        commandsFile = rom + "/" + romName + ".commands"
        singeFile = rom + "/" + romName + ".singe"

        bezelFile = find_bezel(romName.lower())
        if bezelFile is not None:
            bezelFile += ".png"
        else:
            bezelFile = romName.lower() + ".png"
        bezelPath = HYPSEUS_DATA_DIR + "/bezels/" + bezelFile

        # get the first video file from frameFile to determine the resolution
        m2v_filename = self.find_m2v_from_txt(frameFile)

        if m2v_filename:
            eslog.debug("First .m2v file found: {}".format(m2v_filename))
        else:
            eslog.debug("No .m2v files found in the text file.")

        # now get the resolution from the m2v file
        video_path = rom + "/" + m2v_filename
        # check the path exists
        if not path.exists(video_path):
            eslog.debug("Could not find m2v file in path - {}".format(video_path))
            video_path = self.find_file(rom, m2v_filename)

        eslog.debug("Full m2v path is: {}".format(video_path))

        if video_path != None:
            video_resolution = self.get_resolution(video_path)
            eslog.debug("Resolution: {}".format(video_resolution))
            if video_resolution == (0, 0):
                eslog.warning(
                    "Could not determine video resolution, using fallback"
                )

        if system.name == "singe":
            commandArray = [
                HYPSEUS_BIN_PATH,
                "singe",
                "vldp",
                "-retropath",
                "-framefile",
                frameFile,
                "-script",
                singeFile,
                "-fullscreen",
                "-gamepad",
                "-datadir",
                HYPSEUS_DATA_DIR,
                "-singedir",
                SINGE_ROM_DIR,
                "-romdir",
                SINGE_ROM_DIR,
                "-homedir",
                HYPSEUS_DATA_DIR,
            ]
        else:
            commandArray = [
                HYPSEUS_BIN_PATH,
                romName,
                "vldp",
                "-framefile",
                frameFile,
                "-fullscreen",
                "-fastboot",
                "-gamepad",
                "-datadir",
                HYPSEUS_DATA_DIR,
                "-romdir",
                DAPHNE_ROM_DIR,
                "-homedir",
                HYPSEUS_DATA_DIR,
            ]

        # controller config file
        if system.isOptSet("hypseus_joy") and system.getOptBoolean("hypseus_joy"):
            commandArray.extend(["-keymapfile", "custom.ini"])
        else:
            commandArray.extend(["-keymapfile", HYPSEUS_CONFIG_FILE_PATH])

        # Default -fullscreen behaviour respects game aspect ratio
        bezelRequired = False
        xratio = None
        if gameResolution["width"] < gameResolution["height"]:
            width, height = gameResolution["height"], gameResolution["width"]
        else:
            width, height = gameResolution["width"], gameResolution["height"]
        # stretch
        if (
            system.isOptSet("hypseus_ratio")
            and system.config["hypseus_ratio"] == "stretch"
        ):
            commandArray.extend(["-x", str(width), "-y", str(height)])
            bezelRequired = False
            if abs(width / height - 4 / 3) < 0.01:
                xratio = 4 / 3
        # 4:3
        elif (
            system.isOptSet("hypseus_ratio")
            and system.config["hypseus_ratio"] == "force_ratio"
        ):
            commandArray.extend(["-x", str(width), "-y", str(height)])
            commandArray.extend(["-force_aspect_ratio"])
            xratio = 4 / 3
            bezelRequired = True
        # Handle original aspect ratio case
        else:
            # Initialize with safe default values
            video_width = 0
            video_height = 0
            video_resolution: Optional[Tuple[int, int]] = (
                None  # ensures that the variable always exists
            )

            # Safely handle video_resolution
            if (
                isinstance(video_resolution, (tuple, list))
                and len(video_resolution) >= 2
            ):
                video_width, video_height = video_resolution[:2]

            # Only proceed with calculations if we have valid resolution
            if video_width > 0 and video_height > 0:
                try:
                    scaling_factor = height / video_height
                    new_width = video_width * scaling_factor

                    commandArray.extend(["-x", str(new_width), "-y", str(height)])

                    # Check if aspect ratio is approximately 4:3 for bezel
                    if abs(new_width / height - 4 / 3) < 0.01:
                        bezelRequired = True
                        xratio = 4 / 3
                    else:
                        bezelRequired = False

                except ZeroDivisionError:
                    eslog.error("Invalid video height (0) - cannot calculate scaling")
                    video_width = 0  # Force fallback

            # Fallback to stretch mode if resolution wasn't valid
            if video_width <= 0 or video_height <= 0:
                eslog.debug("Using fallback stretch resolution")
                commandArray.extend(["-x", str(width), "-y", str(height)])
                # Check if screen is approximately 4:3
                if abs(width / height - 4 / 3) < 0.01:
                    xratio = 4 / 3

        # Don't set bezel if screeen resolution is not conducive to needing them (i.e. CRT)
        if width / height < 1.51:
            bezelRequired = False

        # Backend - Default OpenGL
        if system.isOptSet("hypseus_api") and system.config["hypseus_api"] == "Vulkan":
            commandArray.append("-vulkan")
        else:
            commandArray.append("-opengl")

        # Enable Bilinear Filtering
        if system.isOptSet("hypseus_filter") and system.getOptBoolean("hypseus_filter"):
            commandArray.append("-linear_scale")

        # The following options should only be set when system is singe.
        # -blend_sprites, -nocrosshair, -sinden or -manymouse
        if system.name == "singe":
            # Blend Sprites (Singe)
            if system.isOptSet("singe_sprites") and system.getOptBoolean(
                "singe_sprites"
            ):
                commandArray.append("-blend_sprites")

            bordersSize = gunsBordersSizeName(guns, system.config)
            if bordersSize is not None:
                borderColor = "w"
                if "controllers.guns.borderscolor" in system.config:
                    borderColorOpt = system.config["controllers.guns.borderscolor"]
                    if borderColorOpt == "white":
                        borderColor = "w"
                    elif borderColorOpt == "red":
                        borderColor = "r"
                    elif borderColorOpt == "green":
                        borderColor = "g"
                    elif borderColorOpt == "blue":
                        borderColor = "b"

                if bordersSize == "thin":
                    commandArray.extend(["-sinden", "2", borderColor])
                elif bordersSize == "medium":
                    commandArray.extend(["-sinden", "4", borderColor])
                else:
                    commandArray.extend(["-sinden", "6", borderColor])
            else:
                if len(guns) > 0:  # enable manymouse for guns
                    commandArray.extend(["-manymouse"])  # sinden implies manymouse
                    if xratio is not None:
                        commandArray.extend(
                            ["-xratio", str(xratio)]
                        )  # accuracy correction based on ratio
                else:
                    if system.isOptSet("singe_abs") and system.getOptBoolean(
                        "singe_abs"
                    ):
                        commandArray.extend(
                            ["-manymouse"]
                        )  # this is causing issues on some "non-gun" games

        # bezels
        if (
            system.isOptSet("hypseus_bezels")
            and system.getOptBoolean("hypseus_bezels") == False
        ):
            bezelRequired = False

        if bezelRequired:
            if not path.exists(bezelPath):
                commandArray.extend(["-bezel", "default.png"])
            else:
                commandArray.extend(["-bezel", bezelFile])

        # Invert HAT Axis
        if system.isOptSet("hypseus_axis") and system.getOptBoolean("hypseus_axis"):
            commandArray.append("-tiphat")

        # Game rotation options for vertical screens, default is 0.
        if (
            system.isOptSet("hypseus_rotate")
            and system.config["hypseus_rotate"] == "90"
        ):
            commandArray.extend(["-rotate", "90"])
        elif (
            system.isOptSet("hypseus_rotate")
            and system.config["hypseus_rotate"] == "270"
        ):
            commandArray.extend(["-rotate", "270"])

        # Singe joystick sensitivity, default is 5.
        if system.name == "singe" and system.isOptSet("singe_joystick_range"):
            commandArray.extend(["-js_range", system.config["singe_joystick_range"]])

        # Scanlines
        if (
            system.isOptSet("hypseus_scanlines")
            and system.config["hypseus_scanlines"] > "0"
        ):
            commandArray.extend(
                ["-scanlines", "-scanline_shunt", system.config["hypseus_scanlines"]]
            )

        # Hide crosshair in supported games (e.g. ActionMax, ALG)
        # needCrosshair
        if len(guns) > 0 and (
            not system.isOptSet("singe_crosshair")
            or (
                system.isOptSet("singe_crosshair")
                and not system.config["singe_crosshair"]
            )
        ):
            commandArray.append("-nocrosshair")

        # Enable SDL_TEXTUREACCESS_STREAMING, can aid SBC's with SDL2 => 2.0.16
        if system.isOptSet("hypseus_texturestream") and system.getOptBoolean(
            "hypseus_texturestream"
        ):
            commandArray.append("-texturestream")

        # The folder may have a file with the game name and .commands with extra arguments to run the game.
        if path.isfile(commandsFile):
            try:
                with open(commandsFile, "r") as f:
                    commandArray.extend(f.read().split())
            except (IOError, OSError) as e:
                eslog.error(f"Error reading commands file {commandsFile}: {e}")

        # We now use SDL controller config
        return Command(
            array=commandArray,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                    playersControllers
                ),
                "SDL_JOYSTICK_HIDAPI": "0",
            },
        )
