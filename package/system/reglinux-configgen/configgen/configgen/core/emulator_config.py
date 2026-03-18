"""Emulator configuration loading utilities for REG-Linux ConfigGen.

This module handles loading and merging configuration from YAML files and other sources.
"""

from pathlib import Path
from typing import Any

import yaml
from yaml import CLoader as Loader

from configgen.utils.logger import get_logger

eslog = get_logger(__name__)

SystemConfigDict = dict[str, Any]


def load_emulator_config(system: str, rom: str) -> SystemConfigDict:
    """Load system-specific configuration, including emulator and core settings.

    Args:
        system: The system name (e.g., 'nes', 'snes').
        rom: Path to the ROM file (used for logging/context).

    Returns:
        System configuration dictionary with emulator, core, and options.

    """
    dict_all = get_generic_config(
        system,
        "/usr/share/reglinux/configgen/configgen-defaults.yml",
        "/usr/share/reglinux/configgen/configgen-defaults-arch.yml",
    )

    # Extract emulator and core, merge options
    dict_result: SystemConfigDict = {
        "emulator": dict_all["emulator"],
        "core": dict_all["core"],
    }
    if "options" in dict_all:
        _dict_merge(dict_result, dict_all["options"])

    return dict_result


def load_render_config(system: str, base_config: SystemConfigDict) -> dict[str, Any]:
    """Load rendering configuration including shaders.

    Args:
        system: The system name.
        base_config: Base emulator configuration (used for shader settings).

    Returns:
        Rendering configuration dictionary.

    """
    renderconfig: dict[str, Any] = {}

    if "shaderset" not in base_config:
        return renderconfig

    shaderset = base_config["shaderset"]

    if shaderset == "none":
        # Use default rendering configs if no shaders are set
        renderconfig = get_generic_config(
            system,
            "/usr/share/reglinux/shaders/configs/rendering-defaults.yml",
            "/usr/share/reglinux/shaders/configs/rendering-defaults-arch.yml",
        )
    else:
        # Prefer user-defined shader configs if available
        user_shader_path = (
            Path("/userdata/shaders/configs") / shaderset / "rendering-defaults.yml"
        )

        if user_shader_path.exists():
            renderconfig = get_generic_config(
                system,
                str(user_shader_path),
                str(
                    Path("/userdata/shaders/configs")
                    / shaderset
                    / "rendering-defaults-arch.yml",
                ),
            )
        else:
            renderconfig = get_generic_config(
                system,
                f"/usr/share/reglinux/shaders/configs/{shaderset}/rendering-defaults.yml",
                f"/usr/share/reglinux/shaders/configs/{shaderset}/rendering-defaults-arch.yml",
            )

    # Load renderer-specific settings for backward compatibility
    from configgen.config.paths import SYSTEM_CONF
    from configgen.settings import UnixSettings

    recalSettings = UnixSettings(SYSTEM_CONF)
    gsname = Path(base_config.get("rom", "")).name if "rom" in base_config else ""

    systemSettings = recalSettings.loadAll(system + "-renderer")
    gameSettings = recalSettings.loadAll(
        system + '["' + gsname + '"]' + "-renderer" if gsname else "",
    )

    # Update renderconfig with renderer settings
    _update_configuration(renderconfig, systemSettings)
    _update_configuration(renderconfig, gameSettings)

    return renderconfig


def get_generic_config(
    system: str,
    defaultyml: str,
    defaultarchyml: str,
) -> dict[str, Any]:
    """Load and merge generic configuration from YAML files.

    Args:
        system: The system name (e.g., 'nes', 'snes').
        defaultyml: Path to the default YAML configuration file.
        defaultarchyml: Path to the architecture-specific YAML configuration file.

    Returns:
        Merged configuration dictionary.

    """
    # Load default configuration
    with Path(defaultyml).open() as f:
        systems_default = yaml.load(f, Loader=Loader) or {}

    # Load architecture-specific configuration if available
    systems_default_arch: dict[str, Any] = {}
    if Path(defaultarchyml).exists():
        with Path(defaultarchyml).open() as f:
            systems_default_arch = yaml.load(f, Loader=Loader) or {}

    dict_all: dict[str, Any] = {}

    # Merge default configurations
    if "default" in systems_default:
        dict_all = systems_default["default"]

    if "default" in systems_default_arch:
        _dict_merge(dict_all, systems_default_arch["default"])

    # Merge system-specific configurations
    if system in systems_default:
        _dict_merge(dict_all, systems_default[system])

    if system in systems_default_arch:
        _dict_merge(dict_all, systems_default_arch[system])

    return dict_all


def _dict_merge(dest: dict[str, Any], src: dict[str, Any]) -> None:
    """Merge src into dest, updating nested dictionaries.

    Args:
        dest: The dictionary to update.
        src: The dictionary to merge into dest.

    """
    stack = [(dest, src)]
    while stack:
        d, s = stack.pop()
        for k, v in s.items():
            if k in d and isinstance(d[k], dict) and isinstance(v, dict):
                stack.append((d[k], v))
            else:
                d[k] = v


def _update_configuration(config: dict[str, Any], settings: dict[str, Any]) -> None:
    """Update a configuration dictionary with new settings, ignoring invalid values.

    Args:
        config: The configuration dictionary to update.
        settings: The new settings to apply.

    """
    # Remove invalid settings ("default", "auto", or empty)
    invalid_settings = [k for k, v in settings.items() if v in ("", "default", "auto")]
    for k in invalid_settings:
        settings.pop(k, None)

    config.update(settings)
