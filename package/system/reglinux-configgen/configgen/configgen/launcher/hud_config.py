"""HUD and Bezel configuration utilities for REG-Linux ConfigGen.

This module contains helper functions for HUD and bezel configuration
that were extracted from the original emulatorlauncher.py.
"""

import contextlib
import json
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

import configgen.bezel.bezel_base as bezels_util
from configgen.core import Emulator
from configgen.utils.logger import get_logger

eslog = get_logger(__name__)


def getHudBezel(
    system: Emulator,
    generator: Any,
    rom: str,
    game_resolution: dict[str, int],
    borders_size: Any = None,
) -> str | None:
    """Determine and prepare the appropriate bezel image for the HUD.

    It checks for bezel compatibility (aspect ratio, coverage) and resizes,
    tattoos, or adds borders to the image as needed.

    Args:
        system: The current system's configuration object.
        generator: The emulator-specific generator.
        rom: Path to the ROM file.
        game_resolution: The current game resolution.
        borders_size: The size of the gun borders, if any.

    Returns:
        The path to the final bezel image file, or None if no bezel should be used.

    """
    # Skip if the emulator handles its own bezels.
    if generator.supportsInternalBezels():
        eslog.debug(f"Skipping bezels for emulator {system.config['emulator']}")
        return None

    # Skip if no bezel is configured and no special effects (tattoo, borders) are needed.
    if (
        ("bezel" not in system.config or system.config["bezel"] in ["", "none"])
        and not (
            system.isOptSet("bezel.tattoo") and system.config["bezel.tattoo"] != "0"
        )
        and borders_size is None
    ):
        return None

    # List of temporary files that may be created
    temp_files: list[str] = []

    try:
        # If no bezel is set but effects are needed, create a transparent base.
        if "bezel" not in system.config or system.config["bezel"] in ["", "none"]:
            with tempfile.NamedTemporaryFile(
                suffix=".png",
                prefix="bezel_transhud_",
                delete=False,
            ) as png_temp:
                overlay_png_file = png_temp.name
            with tempfile.NamedTemporaryFile(
                suffix=".info",
                prefix="bezel_transhud_",
                delete=False,
            ) as info_temp:
                overlay_info_file = info_temp.name

            temp_files.extend([overlay_png_file, overlay_info_file])
            bezels_util.createTransparentBezel(
                overlay_png_file,
                game_resolution["width"],
                game_resolution["height"],
            )

            w, h = game_resolution["width"], game_resolution["height"]
            Path(overlay_info_file).write_text(
                f'{{"width":{w}, "height":{h}, "opacity":1.0, "messagex":0.22, "messagey":0.12}}'
            )
        else:
            # A bezel is configured, so let's find its files.
            eslog.debug(
                f"HUD enabled. Trying to apply the bezel {system.config['bezel']}"
            )
            bezel = system.config["bezel"]
            bezels_util.getBezelInfos(
                rom,
                bezel,
                system.name,
                system.config["emulator"],
            )

            # Get bezel file paths - construct from standard locations
            bezel_dir = Path("/usr/share/reglinux/datainit/decorations") / bezel
            overlay_png_file = str(bezel_dir / f"{bezel}.png")
            overlay_info_file = str(bezel_dir / f"{bezel}.info")

            if not Path(overlay_png_file).exists():
                # Try user bezels
                user_bezel_dir = Path("/userdata/decorations") / bezel
                overlay_png_file = str(user_bezel_dir / f"{bezel}.png")
                overlay_info_file = str(user_bezel_dir / f"{bezel}.info")

            if not Path(overlay_png_file).exists():
                eslog.warning(f"Bezel PNG not found for {bezel}")
                return None

        # --- Bezel Validation ---
        infos = {}
        try:
            if overlay_info_file and isinstance(overlay_info_file, str):
                with Path(overlay_info_file).open() as f:
                    infos = json.load(f)
            else:
                eslog.warning(f"Invalid overlay info file: {overlay_info_file}")
        except FileNotFoundError:
            eslog.warning(f"Bezel info file not found: {overlay_info_file}")
        except json.JSONDecodeError as e:
            eslog.warning(f"Invalid JSON in bezel info file {overlay_info_file}: {e}")
        except Exception as e:
            eslog.warning(f"Unable to read bezel info file {overlay_info_file}: {e}")

        # Get bezel dimensions either from info file or the image itself.
        if "width" in infos and "height" in infos:
            bezel_width: int = infos["width"]
            bezel_height: int = infos["height"]
            eslog.info(f"Bezel size read from {overlay_info_file}")
        elif overlay_png_file and isinstance(overlay_png_file, str):
            bezel_width: int = bezels_util.fast_image_size(overlay_png_file)[0]
            bezel_height: int = bezels_util.fast_image_size(overlay_png_file)[1]
            eslog.info(f"Bezel size read from {overlay_png_file}")
        else:
            eslog.error(f"Invalid overlay PNG file: {overlay_png_file}")
            return None

        # Define validation thresholds.
        max_ratio_delta = 0.01
        screen_ratio: float = game_resolution["width"] / game_resolution["height"]
        bezel_ratio: float = bezel_width / bezel_height

        # Validate aspect ratio (unless gun borders are being added).
        if borders_size is None and abs(screen_ratio - bezel_ratio) > max_ratio_delta:
            eslog.debug(
                f"Screen ratio ({screen_ratio}) is too far from the bezel one ({bezel_ratio})"
            )
            return None

        # --- Bezel Processing ---
        with ThreadPoolExecutor(max_workers=1) as executor:
            # Resize the bezel image if it doesn't match the screen resolution.
            bezel_stretch = system.isOptSet("bezel_stretch") and system.getOptBoolean(
                "bezel_stretch"
            )
            if (
                bezel_width != game_resolution["width"]
                or bezel_height != game_resolution["height"]
            ):
                eslog.debug("Bezel needs to be resized")
                with tempfile.NamedTemporaryFile(
                    suffix=".png",
                    prefix="bezel_resize_",
                    delete=False,
                ) as temp_file:
                    output_png_file = temp_file.name
                temp_files.append(output_png_file)
                if overlay_png_file and isinstance(overlay_png_file, (str, Path)):
                    try:
                        future = executor.submit(
                            bezels_util.resizeImage,
                            str(overlay_png_file),
                            output_png_file,
                            game_resolution["width"],
                            game_resolution["height"],
                            bezel_stretch,
                        )
                        future.result()
                        overlay_png_file = output_png_file
                    except Exception as e:
                        eslog.error(f"Failed to resize the image: {e}")
                        return None
                else:
                    eslog.error(
                        f"Invalid overlay PNG file for resize: {overlay_png_file}"
                    )
                    return None

            # Apply a "tattoo" (watermark/logo) to the bezel if configured.
            if system.isOptSet("bezel.tattoo") and system.config["bezel.tattoo"] != "0":
                with tempfile.NamedTemporaryFile(
                    suffix=".png",
                    prefix="bezel_tattooed_",
                    delete=False,
                ) as temp_file:
                    output_png_file = temp_file.name
                temp_files.append(output_png_file)
                if overlay_png_file and isinstance(overlay_png_file, (str, Path)):
                    future = executor.submit(
                        bezels_util.tatooImage,
                        str(overlay_png_file),
                        output_png_file,
                        system,
                    )
                    future.result()
                    overlay_png_file = output_png_file
                else:
                    eslog.error(
                        f"Invalid overlay PNG file for tattoo: {overlay_png_file}"
                    )
                    return None

            # Draw gun borders on the bezel if required.
            if borders_size is not None:
                eslog.debug("Drawing gun borders")
                with tempfile.NamedTemporaryFile(
                    suffix=".png",
                    prefix="bezel_gunborders_",
                    delete=False,
                ) as temp_file:
                    output_png_file = temp_file.name
                temp_files.append(output_png_file)
                inner_size, outer_size = bezels_util.gun_borders_size(borders_size)
                color = bezels_util.gunsBordersColorFomConfig(system.config)
                if overlay_png_file and isinstance(overlay_png_file, (str, Path)):
                    future = executor.submit(
                        bezels_util.gunBorderImage,
                        str(overlay_png_file),
                        output_png_file,
                        inner_size,
                        outer_size,
                        color,
                    )
                    future.result()
                    overlay_png_file = output_png_file
                else:
                    eslog.error(
                        f"Invalid overlay PNG file for gun border: {overlay_png_file}"
                    )
                    return None

        eslog.debug(f"Applying bezel {overlay_png_file}")
        return overlay_png_file

    except Exception as e:
        eslog.error(f"Error preparing bezel: {e}")
        # Clean up temporary files on error
        for temp_file in temp_files:
            with contextlib.suppress(Exception):
                Path(temp_file).unlink(missing_ok=True)
        return None


def getHudConfig(
    system: Emulator,
    systemName: str,
    emulator: str,
    core: str,
    _rom: str,
    gameinfos: dict[str, str],
    bezel: str | None,
) -> str:
    """Generate the configuration string for MangoHUD.

    Args:
        system: The current system's configuration object.
        systemName: The "fancy" name of the system.
        emulator: The name of the emulator.
        core: The name of the emulator core.
        _rom: Path to the ROM file (currently unused).
        gameinfos: Game metadata (name, thumbnail).
        bezel: Path to the bezel image to be used as a background.

    Returns:
        The complete MangoHUD configuration string.

    """
    configstr = ""

    # Set the bezel as the background image for the HUD.
    if bezel:
        configstr = (
            f"background_image={hudConfig_protectStr(bezel)}\nlegacy_layout=false\n"
        )

    # If HUD is disabled, just make the background transparent.
    if not system.isOptSet("hud") or system.config["hud"] == "none":
        return configstr + "background_alpha=0\n"

    mode = system.config["hud"]

    # Determine HUD position from config.
    position_map = {"NW": "top-left", "NE": "top-right", "SE": "bottom-right"}
    hud_corner = system.config.get("hud_corner", "")
    hud_position = position_map.get(hud_corner, "bottom-left")

    emulatorstr = f"{emulator}/{core}" if emulator != core and core else emulator
    gameName = gameinfos.get("name", "")
    gameThumbnail = gameinfos.get("thumbnail", "")

    # Apply predefined or custom HUD configurations.
    if mode == "perf":
        configstr += (
            f"position={hud_position}\nbackground_alpha=0.9\nlegacy_layout=false\n"
            "fps\ngpu_name\nengine_version\nvulkan_driver\nresolution\nram\n"
            "gpu_stats\ngpu_temp\ncpu_stats\ncpu_temp\ncore_load"
        )
    elif mode == "game":
        configstr += (
            f"position={hud_position}\nbackground_alpha=0\nlegacy_layout=false\n"
            "font_size=32\nimage_max_width=200\nimage=%THUMBNAIL%\n"
            "custom_text=%GAMENAME%\ncustom_text=%SYSTEMNAME%\ncustom_text=%EMULATORCORE%"
        )
    elif (
        mode == "custom"
        and system.isOptSet("hud_custom")
        and system.config["hud_custom"]
    ):
        configstr += system.config["hud_custom"].replace("\\n", "\n")
    else:
        # Fallback to hiding the HUD if the mode is invalid.
        configstr += "background_alpha=0\n"

    # Replace placeholders with actual values.
    configstr = configstr.replace("%SYSTEMNAME%", hudConfig_protectStr(systemName))
    configstr = configstr.replace("%GAMENAME%", hudConfig_protectStr(gameName))
    configstr = configstr.replace("%EMULATORCORE%", hudConfig_protectStr(emulatorstr))
    return configstr.replace("%THUMBNAIL%", hudConfig_protectStr(gameThumbnail))


def extractGameInfosFromXml(
    system_name: str,
    rom: str,
    xml_path: str,
) -> dict[str, str]:
    """Extract game information from XML metadata.

    Args:
        system_name: The system name.
        rom: Path to the ROM file.
        xml_path: Path to the XML metadata file.

    Returns:
        Dictionary of game information.

    """
    metadata: dict[str, str] = {}

    try:
        import xml.etree.ElementTree as ET

        tree = ET.parse(xml_path)
        root = tree.getroot()

        rom_name = Path(rom).stem

        for game in root.findall(".//game"):
            path_elem = game.find("path")
            if (
                path_elem is not None
                and path_elem.text
                and Path(path_elem.text).stem == rom_name
            ):
                # Extract relevant metadata
                for child in game:
                    if child.text:
                        metadata[child.tag] = child.text
                break

    except Exception as e:
        eslog.warning(f"Failed to extract game info from XML: {e}")

    return metadata


def callExternalScripts(
    system: Emulator,
    rom: str,
    event: str,
) -> None:
    """Call external scripts for game events.

    Args:
        system: The emulator configuration.
        rom: Path to the ROM file.
        event: The event type (e.g., 'gameStart', 'gameEnd').

    """
    import subprocess
    from pathlib import Path

    scripts_dir = Path("/userdata/scripts") / event

    if not scripts_dir.exists():
        return

    # Get safe script extensions
    safe_extensions = {".sh", ".py"}

    try:
        for filepath in sorted(scripts_dir.iterdir()):
            if filepath.suffix.lower() in safe_extensions and filepath.is_file():
                eslog.info(f"Calling external script {filepath} for event {event}")
                try:
                    # Make script executable
                    filepath.chmod(0o755)

                    # Execute the script with system, rom, and emulator info
                    result = subprocess.run(
                        [
                            str(filepath),
                            system.name,
                            rom,
                            system.config.get("emulator", ""),
                        ],
                        capture_output=True,
                        text=True,
                        timeout=30,
                    )

                    if result.stdout:
                        eslog.debug(f"Script output: {result.stdout}")
                    if result.returncode != 0:
                        eslog.warning(
                            f"Script {filepath} exited with code {result.returncode}"
                        )
                        if result.stderr:
                            eslog.warning(f"Script stderr: {result.stderr}")

                except subprocess.TimeoutExpired:
                    eslog.error(f"Script {filepath} timed out")
                except Exception as e:
                    eslog.error(f"Error executing script {filepath}: {e}")

    except Exception as e:
        eslog.error(f"Error listing scripts directory: {e}")


def hudConfig_protectStr(text: str) -> str:
    """Return an empty string if the input is None, otherwise return the input.

    Args:
        text: The string to protect.

    Returns:
        The original string or an empty string.

    """
    return text or ""
