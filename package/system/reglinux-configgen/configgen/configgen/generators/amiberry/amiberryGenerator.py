from configgen.generators.Generator import Generator
from configgen.Command import Command
from zipfile import ZipFile
from os import path
from configgen.controllers import generate_sdl_controller_config
from configgen.utils.logger import get_logger
from .amiberryConfig import setAmiberryConfig, AMIBERRY_BIN_PATH

eslog = get_logger(__name__)


class AmiberryGenerator(Generator):
    def generate(
        self, system, rom, playersControllers, metadata, guns, wheels, gameResolution
    ):
        # setting up amiberry config file
        setAmiberryConfig(system)

        romType = self.getRomType(rom)
        if romType != "UNKNOWN":
            commandArray = [AMIBERRY_BIN_PATH, "-G"]
            if romType != "WHDL":
                commandArray.append("--model")
                commandArray.append(system.config["core"])

            if romType == "WHDL":
                commandArray.append("--autoload")
                commandArray.append(rom)
            elif romType == "HDF":
                commandArray.append("-s")
                commandArray.append("hardfile2=rw,DH0:" + rom + ",32,1,2,512,0,,uae0")
                commandArray.append("-s")
                commandArray.append("uaehf0=hdf,rw,DH0:" + rom + ",32,1,2,512,0,,uae0")
            elif romType == "CD":
                commandArray.append("--cdimage")
                commandArray.append(rom)
            elif romType == "DISK":
                # floppies
                n = 0
                for img in self.floppiesFromRom(rom):
                    if n < 4:
                        commandArray.append("-" + str(n))
                        commandArray.append(img)
                    n += 1
                # floppy path
                commandArray.append("-s")
                # Use disk folder as floppy path
                romPathIndex = rom.rfind("/")
                commandArray.append("amiberry.floppy_path=" + rom[0:romPathIndex])

            # fps
            if system.config["showFPS"] == "true":
                commandArray.append("-s")
                commandArray.append("show_leds=true")

            # disable port 2 (otherwise, the joystick goes on it)
            commandArray.append("-s")
            commandArray.append("joyport2=")

            # remove interlace artifacts
            if (
                system.isOptSet("amiberry_flickerfixer")
                and system.config["amiberry_flickerfixer"] == "true"
            ):
                commandArray.append("-s")
                commandArray.append("gfx_flickerfixer=true")
            else:
                commandArray.append("-s")
                commandArray.append("gfx_flickerfixer=false")

            # auto height
            if (
                system.isOptSet("amiberry_auto_height")
                and system.config["amiberry_auto_height"] == "true"
            ):
                commandArray.append("-s")
                commandArray.append("amiberry.gfx_auto_height=true")
            else:
                commandArray.append("-s")
                commandArray.append("amiberry.gfx_auto_height=false")

            # line mode
            if system.isOptSet("amiberry_linemode"):
                if system.config["amiberry_linemode"] == "none":
                    commandArray.append("-s")
                    commandArray.append("gfx_linemode=none")
                elif system.config["amiberry_linemode"] == "scanlines":
                    commandArray.append("-s")
                    commandArray.append("gfx_linemode=scanlines")
                elif system.config["amiberry_linemode"] == "double":
                    commandArray.append("-s")
                    commandArray.append("gfx_linemode=double")
            else:
                commandArray.append("-s")
                commandArray.append("gfx_linemode=double")

            # video resolution
            if system.isOptSet("amiberry_resolution"):
                if system.config["amiberry_resolution"] == "lores":
                    commandArray.append("-s")
                    commandArray.append("gfx_resolution=lores")
                elif system.config["amiberry_resolution"] == "superhires":
                    commandArray.append("-s")
                    commandArray.append("gfx_resolution=superhires")
                elif system.config["amiberry_resolution"] == "hires":
                    commandArray.append("-s")
                    commandArray.append("gfx_resolution=hires")
            else:
                commandArray.append("-s")
                commandArray.append("gfx_resolution=hires")

            # Scaling method
            if system.isOptSet("amiberry_scalingmethod"):
                if system.config["amiberry_scalingmethod"] == "automatic":
                    commandArray.append("-s")
                    commandArray.append("gfx_lores_mode=false")
                    commandArray.append("-s")
                    commandArray.append("amiberry.scaling_method=-1")
                elif system.config["amiberry_scalingmethod"] == "smooth":
                    commandArray.append("-s")
                    commandArray.append("gfx_lores_mode=true")
                    commandArray.append("-s")
                    commandArray.append("amiberry.scaling_method=1")
                elif system.config["amiberry_scalingmethod"] == "pixelated":
                    commandArray.append("-s")
                    commandArray.append("gfx_lores_mode=true")
                    commandArray.append("-s")
                    commandArray.append("amiberry.scaling_method=0")
            else:
                commandArray.append("-s")
                commandArray.append("gfx_lores_mode=false")
                commandArray.append("-s")
                commandArray.append("amiberry.scaling_method=-1")

            # display vertical centering
            commandArray.append("-s")
            commandArray.append("gfx_center_vertical=smart")

            # fix sound buffer and frequency
            commandArray.append("-s")
            commandArray.append("sound_max_buff=4096")
            commandArray.append("-s")
            commandArray.append("sound_frequency=48000")

            return Command(
                array=commandArray,
                env={
                    "XDG_DATA_HOME": "/userdata/system/configs/",
                    "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                        playersControllers
                    ),
                },
            )
        # otherwise, unknown format
        return Command(array=[])

    def floppiesFromRom(self, rom):
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
            prefix = filepath[0:indexDisk + 6]
            postfix = filepath[indexDisk + 7:]
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

    def getRomType(self, filepath):
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
                            eslog.debug(f"File in ZIP: {zipfilename}, extension: {extension}")
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
