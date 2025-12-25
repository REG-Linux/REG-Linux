from os import path
from typing import List
from zipfile import ZipFile

from configgen.Command import Command
from configgen.controllers import generate_sdl_controller_config
from configgen.generators.Generator import Generator
from configgen.utils.logger import get_logger

from .amiberryConfig import AMIBERRY_BIN_PATH, setAmiberryConfig

eslog = get_logger(__name__)


class AmiberryGenerator(Generator):
    def generate(
        self, system, rom, players_controllers, metadata, guns, wheels, game_resolution
    ):
        # setting up amiberry config file
        setAmiberryConfig(system)

        rom_type = self.get_rom_type(rom)
        if rom_type != "UNKNOWN":
            command_array = [AMIBERRY_BIN_PATH, "-G"]
            if rom_type != "WHDL":
                command_array.append("--model")
                command_array.append(system.config["core"])

            if rom_type == "WHDL":
                command_array.append("--autoload")
                command_array.append(rom)
            elif rom_type == "HDF":
                command_array.append("-s")
                command_array.append("hardfile2=rw,DH0:" + rom + ",32,1,2,512,0,,uae0")
                command_array.append("-s")
                command_array.append("uaehf0=hdf,rw,DH0:" + rom + ",32,1,2,512,0,,uae0")
            elif rom_type == "CD":
                command_array.append("--cdimage")
                command_array.append(rom)
            elif rom_type == "DISK":
                # floppies
                n = 0
                for img in self.floppies_from_rom(rom):
                    if n < 4:
                        command_array.append("-" + str(n))
                        command_array.append(img)
                    n += 1
                # floppy path
                command_array.append("-s")
                # Use disk folder as floppy path
                rom_path_index = rom.rfind("/")
                command_array.append("amiberry.floppy_path=" + rom[0:rom_path_index])

            # fps
            if system.config["showFPS"] == "true":
                command_array.append("-s")
                command_array.append("show_leds=true")

            # disable port 2 (otherwise, the joystick goes on it)
            command_array.append("-s")
            command_array.append("joyport2=")

            # remove interlace artifacts
            if (
                system.isOptSet("amiberry_flickerfixer")
                and system.config["amiberry_flickerfixer"] == "true"
            ):
                command_array.append("-s")
                command_array.append("gfx_flickerfixer=true")
            else:
                command_array.append("-s")
                command_array.append("gfx_flickerfixer=false")

            # auto height
            if (
                system.isOptSet("amiberry_auto_height")
                and system.config["amiberry_auto_height"] == "true"
            ):
                command_array.append("-s")
                command_array.append("amiberry.gfx_auto_height=true")
            else:
                command_array.append("-s")
                command_array.append("amiberry.gfx_auto_height=false")

            # line mode
            if system.isOptSet("amiberry_linemode"):
                if system.config["amiberry_linemode"] == "none":
                    command_array.append("-s")
                    command_array.append("gfx_linemode=none")
                elif system.config["amiberry_linemode"] == "scanlines":
                    command_array.append("-s")
                    command_array.append("gfx_linemode=scanlines")
                elif system.config["amiberry_linemode"] == "double":
                    command_array.append("-s")
                    command_array.append("gfx_linemode=double")
            else:
                command_array.append("-s")
                command_array.append("gfx_linemode=double")

            # video resolution
            if system.isOptSet("amiberry_resolution"):
                if system.config["amiberry_resolution"] == "lores":
                    command_array.append("-s")
                    command_array.append("gfx_resolution=lores")
                elif system.config["amiberry_resolution"] == "superhires":
                    command_array.append("-s")
                    command_array.append("gfx_resolution=superhires")
                elif system.config["amiberry_resolution"] == "hires":
                    command_array.append("-s")
                    command_array.append("gfx_resolution=hires")
            else:
                command_array.append("-s")
                command_array.append("gfx_resolution=hires")

            # Scaling method
            if system.isOptSet("amiberry_scalingmethod"):
                if system.config["amiberry_scalingmethod"] == "automatic":
                    command_array.append("-s")
                    command_array.append("gfx_lores_mode=false")
                    command_array.append("-s")
                    command_array.append("amiberry.scaling_method=-1")
                elif system.config["amiberry_scalingmethod"] == "smooth":
                    command_array.append("-s")
                    command_array.append("gfx_lores_mode=true")
                    command_array.append("-s")
                    command_array.append("amiberry.scaling_method=1")
                elif system.config["amiberry_scalingmethod"] == "pixelated":
                    command_array.append("-s")
                    command_array.append("gfx_lores_mode=true")
                    command_array.append("-s")
                    command_array.append("amiberry.scaling_method=0")
            else:
                command_array.append("-s")
                command_array.append("gfx_lores_mode=false")
                command_array.append("-s")
                command_array.append("amiberry.scaling_method=-1")

            # display vertical centering
            command_array.append("-s")
            command_array.append("gfx_center_vertical=smart")

            # fix sound buffer and frequency
            command_array.append("-s")
            command_array.append("sound_max_buff=4096")
            command_array.append("-s")
            command_array.append("sound_frequency=48000")

            return Command(
                array=command_array,
                env={
                    "XDG_DATA_HOME": "/userdata/system/configs/",
                    "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                        players_controllers
                    ),
                },
            )
        # otherwise, unknown format
        return Command(array=[])

    def floppies_from_rom(self, rom: str) -> List[str]:
        floppies = []
        eslog.debug(f"Looking for floppy images for ROM: {rom}")

        # split path and extension
        filepath, fileext = path.splitext(rom)

        #
        indexDisk = filepath.rfind("(Disk 1")

        # from one file (x1.zip), get the list of all existing files with the same extension
        # + last char (as number) suffix
        # for example, "/path/toto0.zip" becomes ["/path/toto0.zip", "/path/toto1.zip", "/path/toto2.zip"]
        if filepath[-1:].isdigit():
            # path without the number
            fileprefix = filepath[:-1]

            # special case for 0 while numerotation can start at 1
            n = 0
            fullfilepath = fileprefix + str(n) + fileext
            if path.isfile(fullfilepath):
                eslog.debug(f"Found floppy image: {fullfilepath}")
                floppies.append(fullfilepath)

            # adding all other files
            n = 1
            while True:
                fullfilepath = fileprefix + str(n) + fileext
                if path.isfile(fullfilepath):
                    eslog.debug(f"Found floppy image: {fullfilepath}")
                    floppies.append(fullfilepath)
                    n += 1
                else:
                    break
        # (Disk 1 of 2) format
        elif indexDisk != -1:
            # Several disks
            floppies.append(rom)
            prefix = filepath[0 : indexDisk + 6]
            postfix = filepath[indexDisk + 7 :]
            n = 2
            while True:
                fullfilepath = prefix + str(n) + postfix + fileext
                if path.isfile(fullfilepath):
                    eslog.debug(f"Found floppy image: {fullfilepath}")
                    floppies.append(fullfilepath)
                    n += 1
                else:
                    break
        else:
            # Single ADF
            eslog.debug("Single ADF file detected")
            return [rom]

        eslog.debug(f"Total floppy images found: {len(floppies)}")
        return floppies

    def get_rom_type(self, filepath: str) -> str:
        eslog.debug(f"Determining ROM type for: {filepath}")
        extension = path.splitext(filepath)[1][1:].lower()

        if extension == "lha":
            eslog.debug("ROM type: WHDL")
            return "WHDL"
        elif extension == "hdf":
            eslog.debug("ROM type: HDF")
            return "HDF"
        elif extension in ["iso", "cue", "chd"]:
            eslog.debug(f"ROM type: CD (extension: {extension})")
            return "CD"
        elif extension in ["adf", "ipf"]:
            eslog.debug(f"ROM type: DISK (extension: {extension})")
            return "DISK"
        elif extension == "zip":
            # can be either whdl or adf
            eslog.debug("Processing ZIP file to determine ROM type")
            try:
                with ZipFile(filepath) as zip_file:
                    for zipfilename in zip_file.namelist():
                        if zipfilename.find("/") == -1:  # at the root
                            extension = path.splitext(zipfilename)[1][1:]
                            eslog.debug(
                                f"File in ZIP: {zipfilename}, extension: {extension}"
                            )
                            if extension == "info":
                                eslog.debug("ROM type: WHDL (found .info file)")
                                return "WHDL"
                            elif extension == "lha":
                                eslog.debug("ROM type: UNKNOWN (found .lha file)")
                                return "UNKNOWN"
                            elif extension == "adf":
                                eslog.debug("ROM type: DISK (found .adf file)")
                                return "DISK"
                # no info or adf file found
                eslog.debug("ROM type: UNKNOWN (no .info/.lha/.adf found in ZIP)")
                return "UNKNOWN"
            except Exception as e:
                eslog.error(f"Error reading ZIP file {filepath}: {str(e)}")
                return "UNKNOWN"

        eslog.debug(f"ROM type: UNKNOWN (extension: {extension})")
        return "UNKNOWN"
