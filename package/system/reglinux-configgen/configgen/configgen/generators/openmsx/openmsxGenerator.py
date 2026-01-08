import re
import shutil
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from typing import Any
from xml.dom import minidom

from configgen.Command import Command
from configgen.generators.Generator import Generator
from configgen.utils.logger import get_logger

eslog = get_logger(__name__)

openMSX_Homedir = Path("/userdata/system/configs/openmsx")
openMSX_Config = Path("/usr/share/openmsx/")


def copy_directory(src: str, dst: str) -> None:
    """Copy all contents from src directory to dst directory, similar to distutils.dir_util.copy_tree.

    This function copies the directory tree from src to dst, creating dst if it doesn't exist
    """
    import shutil
    from pathlib import Path

    src_path = Path(src)
    dst_path = Path(dst)

    eslog.debug(f"Copying directory from {src_path} to {dst_path}")
    if not dst_path.exists():
        eslog.debug(f"Creating destination directory: {dst_path}")
        dst_path.mkdir(parents=True, exist_ok=True)

    for item in src_path.iterdir():
        src_item_path = src_path / item
        dst_item_path = dst_path / item.name

        if src_item_path.is_dir():
            eslog.debug(f"Recursively copying directory: {src_item_path}")
            copy_directory(str(src_item_path), str(dst_item_path))
        else:
            eslog.debug(f"Copying file: {src_item_path}")
            shutil.copy2(src_item_path, dst_item_path)
    eslog.debug(f"Directory copy completed from {src_path} to {dst_path}")


class OpenmsxGenerator(Generator):
    def hasInternalMangoHUDCall(self):
        return True

    def generate(
        self,
        system: Any,
        rom: str,
        players_controllers: Any,
        metadata: Any,
        guns: Any,
        wheels: Any,
        game_resolution: Any,
    ) -> Command:
        share_dir = openMSX_Homedir / "share"
        source_settings = openMSX_Config / "settings.xml"
        settings_xml = share_dir / "settings.xml"
        settings_tcl = share_dir / "script.tcl"

        # create folder if needed
        if not openMSX_Homedir.is_dir():
            openMSX_Homedir.mkdir(parents=True, exist_ok=True)

        # screenshot folder
        screenshot_dir = Path("/userdata/screenshots/openmsx")
        if not screenshot_dir.is_dir():
            screenshot_dir.mkdir(parents=True, exist_ok=True)

        # copy files if needed
        if not share_dir.exists():
            share_dir.mkdir(parents=True, exist_ok=True)
            # Use shutil.copytree with dirs_exist_ok=True to mimic copy_tree behavior
            # For older Python versions that don't support dirs_exist_ok, use a custom function
            copy_directory(str(openMSX_Config), str(share_dir))

        # always use our settings.xml file as a base
        shutil.copy2(source_settings, share_dir)

        # Adjust settings.xml as needed
        tree = ET.parse(settings_xml)
        root = tree.getroot()

        settings_elem = root.find("settings")
        if settings_elem is not None:
            if system.isOptSet("openmsx_loading"):
                fullspeed_elem = ET.Element("setting", {"id": "fullspeedwhenloading"})
                fullspeed_elem.text = system.config["openmsx_loading"]
            else:
                fullspeed_elem = ET.Element("setting", {"id": "fullspeedwhenloading"})
                fullspeed_elem.text = "true"

            settings_elem.append(fullspeed_elem)
        else:
            # Log the error but continue processing
            eslog.warning(
                "Could not find 'settings' element in XML, skipping fullspeedwhenloading setting",
            )

        # Create the bindings element
        bindings_elem = ET.Element("bindings")
        new_bind = ET.Element("bind", {"key": "keyb F6"})
        new_bind.text = "cycle videosource"

        # Add new_bind to bindings_elem (this is safe since we just created bindings_elem)
        bindings_elem.append(new_bind)

        # Add the bindings element to the root element only if both exist
        if root is not None:
            root.append(bindings_elem)
        else:
            eslog.warning("Could not add bindings to root element")

        # Write the updated xml to the file
        with open(settings_xml, "w") as f:
            f.write("<!DOCTYPE settings SYSTEM 'settings.dtd'>\n")
            # purdify the XML
            xml_string = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
            formatted_xml = "\n".join(
                [line for line in xml_string.split("\n") if line.strip()],
            )
            f.write(formatted_xml)

        # setup the blank tcl file
        with open(settings_tcl, "w") as file:
            file.write("")

        # set the tcl file options - we can add other options later
        with open(settings_tcl, "a") as file:
            file.write(
                "filepool add -path /userdata/bios/Machines -types system_rom -position 1\n",
            )
            file.write(
                "filepool add -path /userdata/bios/openmsx -types system_rom -position 2\n",
            )
            # get the rom name (no extension) for the savestate name
            save_name = Path(rom).name
            save_name = Path(rom).stem
            # simplify the rom name, remove content between brackets () & []
            save_name = re.sub(r"\([^)]*\)", "", save_name)
            save_name = re.sub(r"\[[^]]*\]", "", save_name)
            file.write("\n")
            file.write("# -= Save state =-\n")
            file.write(f'savestate "{save_name}"\n')
            # set the screenshot
            file.write("\n")
            file.write("# -= Screenshots =-\n")
            file.write(
                f'bind F5 {{screenshot [utils::get_next_numbered_filename {screenshot_dir} "[guess_title] " ".png"]}}\n',
            )
            # setup the controller
            file.write("\n")
            file.write("# -= Controller config =-\n")
            nplayer = 1
            for _, pad in sorted(players_controllers.items()):
                if nplayer <= 2:
                    if nplayer == 1:
                        file.write("plug joyporta joystick1\n")
                    if nplayer == 2:
                        file.write("plug joyportb joystick2\n")
                    for x in pad.inputs:
                        input_obj = pad.inputs[x]
                        if input_obj.name == "y":
                            file.write(
                                f'bind "joy{nplayer} button{input_obj.id} down" "keymatrixdown 6 0x40"\n',
                            )
                        if input_obj.name == "x":
                            file.write(
                                f'bind "joy{nplayer} button{input_obj.id} down" "keymatrixdown 6 0x80"\n',
                            )
                        if input_obj.name == "pagedown":
                            file.write(
                                f'bind "joy{nplayer} button{input_obj.id} up" "set fastforward off"\n',
                            )
                            file.write(
                                f'bind "joy{nplayer} button{input_obj.id} down" "set fastforward on"\n',
                            )
                        if input_obj.name == "select":
                            file.write(
                                f'bind "joy{nplayer} button{input_obj.id} down" "toggle pause"\n',
                            )
                        if input_obj.name == "start":
                            file.write(
                                f'bind "joy{nplayer} button{input_obj.id} down" "main_menu_toggle"\n',
                            )
                        if input_obj.name == "l3":
                            file.write(
                                f'bind "joy{nplayer} button{input_obj.id} down" "toggle_osd_keyboard"\n',
                            )
                        if input_obj.name == "r3":
                            file.write(
                                f'bind "joy{nplayer} button{input_obj.id} down" "toggle console"\n',
                            )
                nplayer += 1

        # now run the rom with the appropriate flags
        file_extension = Path(rom).suffix.lower()
        command_array = ["/usr/bin/openmsx", "-cart", rom, "-script", settings_tcl]

        # set the best machine based on the system
        if system.name in ["msx1", "msx2"]:
            command_array[1:1] = ["-machine", "Boosted_MSX2_EN"]

        if system.name == "msx2+":
            command_array[1:1] = ["-machine", "Boosted_MSX2+_JP"]

        if system.name == "msxturbor":
            command_array[1:1] = ["-machine", "Boosted_MSXturboR_with_IDE"]

        if system.name == "colecovision":
            command_array[1:1] = ["-machine", "ColecoVision_SGM"]

        if system.name == "spectravideo":
            command_array[1:1] = ["-machine", "Spectravideo_SVI-328"]

        if (
            system.isOptSet("hud")
            and Path("/usr/bin/mangohud").exists()
            and system.config["hud"] != ""
        ):
            command_array.insert(0, "mangohud")

        # setup the media types
        if file_extension == ".zip":
            with zipfile.ZipFile(rom, "r") as zip_file:
                for zip_info in zip_file.infolist():
                    file_extension = Path(zip_info.filename).suffix
                    # usually zip files only contain 1 file however break loop if file extension found
                    if file_extension in [".cas", ".dsk", ".ogv"]:
                        eslog.debug(f"Zip file contains: {file_extension}")
                        break

        if file_extension == ".ogv":
            eslog.debug("File is a laserdisc")
            for i in range(len(command_array)):
                if command_array[i] == "-machine":
                    command_array[i + 1] = "Pioneer_PX-7"
                elif command_array[i] == "-cart":
                    command_array[i] = "-laserdisc"

        if file_extension == ".cas":
            eslog.debug("File is a cassette")
            for i in range(len(command_array)):
                if command_array[i] == "-cart":
                    command_array[i] = "-cassetteplayer"

        if file_extension == ".dsk":
            eslog.debug("File is a disk")
            disk_type = "-diska"
            if (
                system.isOptSet("openmsx_disk")
                and system.config["openmsx_disk"] == "hda"
            ):
                disk_type = "-hda"
            for i in range(len(command_array)):
                if command_array[i] == "-cart":
                    command_array[i] = disk_type

        # handle our own file format for stacked roms / disks
        if file_extension == ".openmsx":
            # read the contents of the file and extract the rom paths
            with open(rom) as file:
                lines = file.readlines()
                rom1 = ""
                rom1 = lines[0].strip()
                rom2 = ""
                rom2 = lines[1].strip()
            # get the directory path of the .openmsx file
            openmsx_dir = Path(rom).parent
            # prepend the directory path to the .rom/.dsk file paths
            rom1 = str(openmsx_dir / rom1)
            rom2 = str(openmsx_dir / rom2)
            # get the first lines extension
            extension = rom1.split(".")[-1].lower()
            # now start ammending the array
            if extension == "rom":
                cart_index = command_array.index("-cart")
                command_array[cart_index] = "-carta"
                command_array[cart_index + 1] = rom1
                # Add the second rom/disk
                rom2_index = cart_index + 2
                command_array.insert(rom2_index, "-cartb")
                command_array.insert(rom2_index + 1, rom2)
            elif extension == "dsk":
                cart_index = command_array.index("-cart")
                command_array[cart_index] = "-diska"
                command_array[cart_index + 1] = rom1
                # Add the second disk
                rom2_index = cart_index + 2
                command_array.insert(rom2_index, "-diskb")
                command_array.insert(rom2_index + 1, rom2)

        return Command(array=command_array)
