"""Simplified module responsible for managing bezel configurations for the Libretro emulator.
"""

from typing import Any

from configgen.bezel.bezel_base import IBezelManager
from configgen.bezel.bezel_common import (
    writeBezelConfig,
)


class LibretroBezelManager(IBezelManager):
    """Bezel manager specific to the Libretro emulator."""

    def setup_bezels(
        self, system: Any, rom: str, game_resolution: dict[str, int], guns: list[Any],
    ) -> None:
        """Configure the bezels for a specific game.

        Args:
            system: System configuration object
            rom: Path to the ROM file
            game_resolution: Dictionary containing game resolution (width, height)
            guns: Guns configuration

        """
        # Libretro-specific implementation would go here
        # For now, we use common functionality
        from configgen.GeneratorImporter import getGenerator

        generator = getGenerator("libretro")

        # Extract bezel settings from system configuration
        bezel = system.config.get("bezel") if system.config.get("bezel") != "" else None
        shader_bezel = system.config.get("shader_bezel", False)
        guns_borders_size = (
            getattr(guns, "borders_size", None) if guns is not None else None
        )

        # Create a default retroarch_config dict if needed
        retroarch_config = {}

        writeBezelConfig(
            generator,
            bezel,
            shader_bezel,
            retroarch_config,
            rom,
            game_resolution,
            system,
            guns_borders_size,
        )
