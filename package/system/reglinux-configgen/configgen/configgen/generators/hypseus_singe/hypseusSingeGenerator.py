from filecmp import cmp
from os import listdir, mkdir, path, walk
from shutil import copy2, copyfile, copytree
from typing import Any, Dict, Optional

from ffmpeg import probe

from configgen.Command import Command
from configgen.controllers import generate_sdl_controller_config, guns_borders_size_name
from configgen.generators.Generator import Generator
from configgen.systemFiles import CONF, ROMS, SAVES
from configgen.utils.logger import get_logger

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
    def find_m2v_from_txt(txt_file: str) -> Optional[str]:
        with open(txt_file) as file:
            for line in file:
                parts = line.strip().split()
                if parts:
                    filename = parts[-1]
                    if filename.endswith(".m2v"):
                        return filename
        return None

    @staticmethod
    def find_file(start_path: str, filename: str) -> Optional[str]:
        if path.exists(path.join(start_path, filename)):
            return path.join(start_path, filename)

        for root, _, files in walk(start_path):
            if filename in files:
                eslog.debug(f"Found m2v file in path - {path.join(root, filename)}")
                return path.join(root, filename)

        return None

    @staticmethod
    def get_resolution(video_path: str) -> Any:
        try:
            # Try to get video information
            probe_video = probe(video_path)
            if not probe_video or "streams" not in probe_video:
                eslog.debug(f"Could not parse the video file: {video_path}")
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
        self,
        system: Any,
        rom: str,
        players_controllers: Any,
        metadata: Any,
        guns: Any,
        wheels: Any,
        game_resolution: Dict[str, int],
    ) -> Command:
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

        def find_bezel(rom_name: str) -> Optional[str]:
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
        def copy_resources(source_dir: str, destination_dir: str) -> None:
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
            eslog.debug(f"First .m2v file found: {m2v_filename}")
        else:
            eslog.debug("No .m2v files found in the text file.")

        # now get the resolution from the m2v file
        if m2v_filename is not None:
            video_path = rom + "/" + m2v_filename
            # check the path exists
            if not path.exists(video_path):
                eslog.debug(f"Could not find m2v file in path - {video_path}")
                video_path = self.find_file(rom, m2v_filename)
        else:
            eslog.debug("m2v file not found, skipping resolution check")
            video_path = None

        if video_path is not None:
            video_resolution = self.get_resolution(video_path)
            eslog.debug(f"Resolution: {video_resolution}")
            if video_resolution == (0, 0):
                eslog.warning("Could not determine video resolution, using fallback")
        else:
            video_resolution = None

        if system.name == "singe":
            command_array = [
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
            command_array = [
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
            command_array.extend(["-keymapfile", "custom.ini"])
        else:
            command_array.extend(["-keymapfile", HYPSEUS_CONFIG_FILE_PATH])

        # Default -fullscreen behaviour respects game aspect ratio
        bezelRequired = False
        xratio = None
        if game_resolution["width"] < game_resolution["height"]:
            width, height = game_resolution["height"], game_resolution["width"]
        else:
            width, height = game_resolution["width"], game_resolution["height"]
        # stretch
        if (
            system.isOptSet("hypseus_ratio")
            and system.config["hypseus_ratio"] == "stretch"
        ):
            command_array.extend(["-x", str(width), "-y", str(height)])
            bezelRequired = False
            if abs(width / height - 4 / 3) < 0.01:
                xratio = 4 / 3
        # 4:3
        elif (
            system.isOptSet("hypseus_ratio")
            and system.config["hypseus_ratio"] == "force_ratio"
        ):
            command_array.extend(["-x", str(width), "-y", str(height)])
            command_array.extend(["-force_aspect_ratio"])
            xratio = 4 / 3
            bezelRequired = True
        # Handle original aspect ratio case
        else:
            # Initialize with safe default values
            video_width = 0
            video_height = 0
            video_resolution: tuple[int, int] | None = (
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

                    command_array.extend(["-x", str(new_width), "-y", str(height)])

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
                command_array.extend(["-x", str(width), "-y", str(height)])
                # Check if screen is approximately 4:3
                if abs(width / height - 4 / 3) < 0.01:
                    xratio = 4 / 3

        # Don't set bezel if screeen resolution is not conducive to needing them (i.e. CRT)
        if width / height < 1.51:
            bezelRequired = False

        # Backend - Default OpenGL
        if system.isOptSet("hypseus_api") and system.config["hypseus_api"] == "Vulkan":
            command_array.append("-vulkan")
        else:
            command_array.append("-opengl")

        # Enable Bilinear Filtering
        if system.isOptSet("hypseus_filter") and system.getOptBoolean("hypseus_filter"):
            command_array.append("-linear_scale")

        # The following options should only be set when system is singe.
        # -blend_sprites, -nocrosshair, -sinden or -manymouse
        if system.name == "singe":
            # Blend Sprites (Singe)
            if system.isOptSet("singe_sprites") and system.getOptBoolean(
                "singe_sprites"
            ):
                command_array.append("-blend_sprites")

            borders_size = guns_borders_size_name(guns, system.config)
            if borders_size is not None:
                border_color = "w"
                if "controllers.guns.borderscolor" in system.config:
                    border_color_opt = system.config["controllers.guns.borderscolor"]
                    if border_color_opt == "white":
                        border_color = "w"
                    elif border_color_opt == "red":
                        border_color = "r"
                    elif border_color_opt == "green":
                        border_color = "g"
                    elif border_color_opt == "blue":
                        border_color = "b"

                if borders_size == "thin":
                    command_array.extend(["-sinden", "2", border_color])
                elif borders_size == "medium":
                    command_array.extend(["-sinden", "4", border_color])
                else:
                    command_array.extend(["-sinden", "6", border_color])
            else:
                if len(guns) > 0:  # enable manymouse for guns
                    command_array.extend(["-manymouse"])  # sinden implies manymouse
                    if xratio is not None:
                        command_array.extend(
                            ["-xratio", str(xratio)]
                        )  # accuracy correction based on ratio
                else:
                    if system.isOptSet("singe_abs") and system.getOptBoolean(
                        "singe_abs"
                    ):
                        command_array.extend(
                            ["-manymouse"]
                        )  # this is causing issues on some "non-gun" games

        # bezels
        if system.isOptSet("hypseus_bezels") and not system.getOptBoolean(
            "hypseus_bezels"
        ):
            bezelRequired = False

        if bezelRequired:
            if not path.exists(bezelPath):
                command_array.extend(["-bezel", "default.png"])
            else:
                command_array.extend(["-bezel", bezelFile])

        # Invert HAT Axis
        if system.isOptSet("hypseus_axis") and system.getOptBoolean("hypseus_axis"):
            command_array.append("-tiphat")

        # Game rotation options for vertical screens, default is 0.
        if (
            system.isOptSet("hypseus_rotate")
            and system.config["hypseus_rotate"] == "90"
        ):
            command_array.extend(["-rotate", "90"])
        elif (
            system.isOptSet("hypseus_rotate")
            and system.config["hypseus_rotate"] == "270"
        ):
            command_array.extend(["-rotate", "270"])

        # Singe joystick sensitivity, default is 5.
        if system.name == "singe" and system.isOptSet("singe_joystick_range"):
            command_array.extend(["-js_range", system.config["singe_joystick_range"]])

        # Scanlines
        if (
            system.isOptSet("hypseus_scanlines")
            and system.config["hypseus_scanlines"] > "0"
        ):
            command_array.extend(
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
            command_array.append("-nocrosshair")

        # Enable SDL_TEXTUREACCESS_STREAMING, can aid SBC's with SDL2 => 2.0.16
        if system.isOptSet("hypseus_texturestream") and system.getOptBoolean(
            "hypseus_texturestream"
        ):
            command_array.append("-texturestream")

        # The folder may have a file with the game name and .commands with extra arguments to run the game.
        if path.isfile(commandsFile):
            try:
                with open(commandsFile) as f:
                    command_array.extend(f.read().split())
            except OSError as e:
                eslog.error(f"Error reading commands file {commandsFile}: {e}")

        # We now use SDL controller config
        return Command(
            array=command_array,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                    players_controllers
                ),
                "SDL_JOYSTICK_HIDAPI": "0",
            },
        )
