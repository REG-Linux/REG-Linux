from filecmp import dircmp
from os import environ
from pathlib import Path
from shutil import copy2
from subprocess import CalledProcessError, check_output
from sys import exit

from configgen.Command import Command
from configgen.controllers import generate_sdl_controller_config
from configgen.generators.Generator import Generator
from configgen.systemFiles import CONF, HOME, SAVES

try:
    from toml import dump, load
except ImportError:
    print("toml module not found. Please install it with: pip install toml")
    raise
from glob import glob
from re import IGNORECASE, search, sub
from typing import Any

from configgen.utils.logger import get_logger

eslog = get_logger(__name__)

XENIA_CONFIG_DIR = CONF / "xenia"
XENIA_CACHE_DIR = HOME / "cache" / "xenia"
XENIA_SAVES_DIR = SAVES / "xbox360"
XENIA_CANARY_BIN_PATH = Path("/usr/bin/xenia_canary")


class XeniaGenerator(Generator):
    # this emulator/core requires a X server to run
    def requiresX11(self):
        return True

    @staticmethod
    def sync_directories(source_dir: str, dest_dir: str) -> None:
        dcmp = dircmp(source_dir, dest_dir)
        # Files that are only in the source directory or are different
        differing_files = dcmp.diff_files + dcmp.left_only
        for file in differing_files:
            src_path = Path(source_dir) / file
            dest_path = Path(dest_dir) / file
            # Copy and overwrite the files from source to destination
            copy2(src_path, dest_path)

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
        core = system.config["core"]

        # check Vulkan first before doing anything
        try:
            have_vulkan = check_output(
                ["/usr/bin/system-vulkan", "hasVulkan"],
                text=True,
            ).strip()
            if have_vulkan == "true":
                eslog.debug("Vulkan driver is available on the system.")
                try:
                    vulkan_version = check_output(
                        ["/usr/bin/system-vulkan", "vulkanVersion"],
                        text=True,
                    ).strip()
                    if vulkan_version > "1.3":
                        eslog.debug(f"Using Vulkan version: {vulkan_version}")
                    elif (
                        system.isOptSet("xenia_api")
                        and system.config["xenia_api"] == "D3D12"
                    ):
                        eslog.debug(
                            f"Vulkan version: {vulkan_version} is not compatible with Xenia when using D3D12",
                        )
                        eslog.debug(
                            f"You may have performance & graphical errors, switching to native Vulkan {vulkan_version}",
                        )
                        system.config["xenia_api"] = "Vulkan"
                    else:
                        eslog.debug(
                            f"Vulkan version: {vulkan_version} is not recommended with Xenia",
                        )
                except CalledProcessError:
                    eslog.debug("Error checking for Vulkan version.")
            else:
                eslog.debug(
                    "*** Vulkan driver required is not available on the system!!! ***",
                )
                exit()
        except CalledProcessError:
            eslog.debug("Error executing system-vulkan script.")

        if not XENIA_CONFIG_DIR.exists():
            XENIA_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        if not XENIA_CACHE_DIR.exists():
            XENIA_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        if not XENIA_SAVES_DIR.exists():
            XENIA_SAVES_DIR.mkdir(parents=True, exist_ok=True)

        # are we loading a digital title?
        if Path(rom).suffix == ".xbox360":
            eslog.debug(f"Found .xbox360 playlist: {rom}")
            pathLead = Path(rom).parent
            try:
                with open(rom) as openFile:
                    # Read only the first line of the file.
                    firstLine = openFile.readlines(1)[0]
                    # Strip of any new line characters.
                    firstLine = firstLine.strip("\n").strip("\r")
                eslog.debug(
                    "Checking if specified disc installation / XBLA file actually exists...",
                )
                xblaFullPath = pathLead / firstLine
                if xblaFullPath.exists():
                    eslog.debug(f"Found! Switching active rom to: {firstLine}")
                    rom = str(xblaFullPath)
                else:
                    eslog.error(
                        f"Disc installation/XBLA title {firstLine} from {rom} not found, check path or filename.",
                    )
            except (OSError, IndexError) as e:
                eslog.error(f"Error reading .xbox360 playlist file {rom}: {e}")
                # Ensure we handle the case where the file might be empty or inaccessible

        # adjust the config toml file accordingly
        config = {}
        if core == "xenia-canary":
            toml_file = XENIA_CONFIG_DIR / "xenia-canary.config.toml"
        else:
            toml_file = XENIA_CONFIG_DIR / "xenia.config.toml"
        if toml_file.is_file():
            with open(toml_file) as f:
                config = load(f)

        # [ Now adjust the config file defaults & options we want ]
        # add node CPU
        if "CPU" not in config:
            config["CPU"] = {}
        # hack, needed for certain games
        config["CPU"] = {"break_on_unimplemented_instructions": False}
        # add node Content
        if "Content" not in config:
            config["Content"] = {}
        # Default 1= First license enabled. Generally the full version license in Xbox Live Arcade (XBLA) titles.
        if system.isOptSet("xeniaLicense"):
            config["Content"] = {"license_mask": int(system.config["xeniaLicense"])}
        else:
            config["Content"] = {"license_mask": 1}
        # add node D3D12
        if "D3D12" not in config:
            config["D3D12"] = {}
        config["D3D12"] = {"d3d12_readback_resolve": True}
        # add node Display
        if "Display" not in config:
            config["Display"] = {}
        # always run fullscreen & set internal resolution - default 1280x720
        displayRes = 8
        if system.isOptSet("xeniaResolution"):
            displayRes = int(system.config["xeniaResolution"])
        config["Display"] = {
            "fullscreen": True,
            "internal_display_resolution": displayRes,
        }
        # add node GPU
        if "GPU" not in config:
            config["GPU"] = {}
        # may be used to bypass fetch constant type errors in certain games.
        # set the API to use
        if system.isOptSet("xenia_api") and system.config["xenia_api"] == "Vulkan":
            config["GPU"] = {
                "depth_float24_convert_in_pixel_shader": True,
                "gpu": "vulkan",
                "gpu_allow_invalid_fetch_constants": True,
                "render_target_path_vulkan": "any",
            }
        else:
            config["GPU"] = {
                "depth_float24_convert_in_pixel_shader": True,
                "gpu_allow_invalid_fetch_constants": True,
                "gpu": "d3d12",
                "render_target_path_d3d12": "rtv",
            }
        # vsync
        config["GPU"]["vsync"] = system.config.get("xenia_vsync", False)
        config["GPU"]["vsync_fps"] = int(system.config.get("xenia_vsync_fps", 60))
        # page state
        config["GPU"]["clear_memory_page_state"] = system.config.get(
            "xenia_page_state",
            False,
        )
        # render target path
        config["GPU"]["render_target_path_d3d12"] = system.config.get(
            "xenia_target_path",
            "rtv",
        )
        # query occlusion
        config["GPU"]["query_occlusion_fake_sample_count"] = int(
            system.config.get("xenia_query_occlusion", 1000),
        )
        # readback resolve
        config["GPU"]["d3d12_readback_resolve"] = system.config.get(
            "xenia_readback_resolve",
            False,
        )
        # cache
        config["GPU"]["texture_cache_memory_limit_hard"] = int(
            system.config.get("xenia_limit_hard", 768),
        )
        config["GPU"]["texture_cache_memory_limit_render_to_texture"] = int(
            system.config.get("xenia_limit_render_to_texture", 24),
        )
        config["GPU"]["texture_cache_memory_limit_soft"] = int(
            system.config.get("xenia_limit_soft", 384),
        )
        config["GPU"]["texture_cache_memory_limit_soft_lifetime"] = int(
            system.config.get("xenia_limit_soft_lifetime", 30),
        )
        # add node General
        if "General" not in config:
            config["General"] = {}
        # disable discord
        config["General"]["discord"] = False
        # patches
        if system.isOptSet("xeniaPatches") and system.config["xeniaPatches"] == "True":
            config["General"] = {"apply_patches": True}
        else:
            config["General"] = {"apply_patches": False}
        # add node HID
        if "HID" not in config:
            config["HID"] = {}
        # ensure we use sdl for controllers
        config["HID"] = {"hid": "sdl"}
        # add node Logging
        if "Logging" not in config:
            config["Logging"] = {}
        # reduce log spam
        config["Logging"] = {"log_level": 1}
        # add node Memory
        if "Memory" not in config:
            config["Memory"] = {}
        # certain games require this to set be set to false to work around crashes.
        config["Memory"] = {"protect_zero": False}
        # add node Storage
        if "Storage" not in config:
            config["Storage"] = {}
        # certain games require this to set be set to true to work around crashes.
        config["Storage"] = {
            "cache_root": XENIA_CACHE_DIR,
            "content_root": XENIA_SAVES_DIR,
            "mount_scratch": True,
            "storage_root": XENIA_CONFIG_DIR,
        }
        # mount cache
        config["Storage"]["mount_cache"] = system.config.get("xenia_cache", False)

        # add node UI
        if "UI" not in config:
            config["UI"] = {}
        # run headless ?
        if system.isOptSet("xeniaHeadless") and system.getOptBoolean("xeniaHeadless"):
            config["UI"] = {"headless": True}
        else:
            config["UI"] = {"headless": False}
        # add node Vulkan
        if "Vulkan" not in config:
            config["Vulkan"] = {}
        config["Vulkan"] = {"vulkan_sparse_shared_memory": False}
        # add node XConfig
        if "XConfig" not in config:
            config["XConfig"] = {}
        # language
        if system.isOptSet("xeniaLanguage"):
            config["XConfig"] = {"user_language": int(system.config["xeniaLanguage"])}
        else:
            config["XConfig"] = {"user_language": 1}

        # now write the updated toml
        with open(toml_file, "w") as f:
            dump(config, f)

        # handle patches files to set all matching toml files keys to true
        rom_name = Path(rom).stem
        # simplify the name for matching
        rom_name = sub(r"\[.*?\]", "", rom_name)
        rom_name = sub(r"\(.*?\)", "", rom_name)
        if system.isOptSet("xeniaPatches") and system.config["xeniaPatches"] == "True":
            # pattern to search for matching .patch.toml files
            pattern = str(XENIA_CONFIG_DIR / "patches" / f"*{rom_name}*.patch.toml")
            matching_files = [
                file_path
                for file_path in glob(pattern)
                if search(rom_name, Path(file_path).name, IGNORECASE)
            ]
            if matching_files:
                for file_path in matching_files:
                    eslog.debug(f"Enabling patches for: {file_path}")
                    # load the matchig .patch.toml file
                    with open(file_path) as f:
                        patch_toml = load(f)
                    # modify all occurrences of the `is_enabled` key to `true`
                    for patch in patch_toml.get("patch", []):
                        if "is_enabled" in patch:
                            patch["is_enabled"] = True
                    # save the updated .patch.toml file
                    with open(file_path, "w") as f:
                        dump(patch_toml, f)
            else:
                eslog.debug(f"No patch file found for {rom_name}")

        # now setup the command array for the emulator
        if rom == "config":
            if core == "xenia-canary":
                command_array = [str(XENIA_CANARY_BIN_PATH)]
            else:
                command_array = ["xenia.exe"]
        elif core == "xenia-canary":
            command_array = [str(XENIA_CANARY_BIN_PATH), "z:" + rom]
        else:
            command_array = ["xenia.exe", "z:" + rom]

        environment = {
            "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                players_controllers,
            ),
            "VKD3D_SHADER_CACHE_PATH": str(XENIA_CACHE_DIR),
        }

        # ensure nvidia driver used for vulkan
        if Path("/var/tmp/nvidia.prime").exists():
            variables_to_remove = [
                "__NV_PRIME_RENDER_OFFLOAD",
                "__VK_LAYER_NV_optimus",
                "__GLX_VENDOR_LIBRARY_NAME",
            ]
            for variable_name in variables_to_remove:
                if variable_name in environ:
                    del environ[variable_name]

            environment.update(
                {
                    "VK_ICD_FILENAMES": "/usr/share/vulkan/icd.d/nvidia_icd.x86_64.json",
                    "VK_LAYER_PATH": "/usr/share/vulkan/explicit_layer.d",
                },
            )

        return Command(array=command_array, env=environment)

    # Show mouse on screen when needed
    # xenia auto-hides
    def getMouseMode(self, config, rom):
        return True
