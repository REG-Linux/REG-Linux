"""Generator Factory for REG-Linux ConfigGen.

This module provides factory functionality for dynamically loading and caching
generator instances for various emulators.
"""

import pathlib
from contextlib import suppress
from importlib import import_module
from threading import Lock
from typing import TYPE_CHECKING

from configgen.factory.mapping import (
    COMMON_RESOURCE_INTENSIVE_EMULATORS,
    EMULATOR_MAPPING,
)

if TYPE_CHECKING:
    from configgen.generators.generator import Generator


class GeneratorNotFoundError(Exception):
    """Exception raised when no generator is found for the specified emulator."""


class GeneratorFactory:
    """Factory for creating and caching generator instances.

    This class implements thread-safe lazy loading of generator classes with
    automatic caching for improved performance.
    """

    _cache: dict[str, type["Generator"]] = {}
    _lock = Lock()

    @classmethod
    def create(cls, emulator: str) -> "Generator":
        """Create a generator instance for the specified emulator.

        Args:
            emulator: The name of the emulator for which to retrieve the generator.

        Returns:
            An instance of the generator class corresponding to the emulator.

        Raises:
            GeneratorNotFoundError: If no generator is found for the specified emulator.

        """
        # Fast path: check if already cached (no lock needed for read)
        generator_class = cls._cache.get(emulator)
        if generator_class is not None:
            return generator_class()

        # Slow path: load the generator class with lock protection
        with cls._lock:
            # Double-check after acquiring lock (another thread may have loaded it)
            generator_class = cls._cache.get(emulator)
            if generator_class is not None:
                return generator_class()

            try:
                generator_class = cls._load_generator_class(emulator)
            except ImportError as e:
                raise GeneratorNotFoundError(
                    f"Failed to import generator for {emulator}: {e}",
                ) from e
            except AttributeError as e:
                raise GeneratorNotFoundError(
                    f"Generator class not found for {emulator}: {e}",
                ) from e

            return generator_class()

    @classmethod
    def _load_generator_class(cls, emulator: str) -> type["Generator"]:
        """Load a generator class from its module.

        Args:
            emulator: The name of the emulator.

        Returns:
            The generator class for the emulator.

        Raises:
            GeneratorNotFoundError: If no generator mapping exists for the emulator.

        """
        try:
            module_path, class_name = EMULATOR_MAPPING[emulator]
        except KeyError:
            raise GeneratorNotFoundError(
                f"No generator found for emulator {emulator}",
            ) from None

        module = import_module(module_path)

        # Validate that the module contains the expected class
        if not hasattr(module, class_name):
            raise GeneratorNotFoundError(
                f"Class {class_name} not found in module {module_path}",
            )

        gen_class = getattr(module, class_name)

        # Cache the loaded class for future use
        cls._cache[emulator] = gen_class
        return gen_class

    @classmethod
    def preload(cls, emulators: set[str] | None = None) -> None:
        """Preload generators into cache to reduce latency on first use.

        Args:
            emulators: Set of emulator names to preload. If None, uses default set.

        """
        if emulators is None:
            emulators = COMMON_RESOURCE_INTENSIVE_EMULATORS

        for emulator in emulators:
            if emulator in EMULATOR_MAPPING and emulator not in cls._cache:
                with suppress(ImportError, AttributeError), cls._lock:
                    cls._load_generator_class(emulator)

    @classmethod
    def clear_cache(cls) -> None:
        """Clear the generator cache. Useful for testing."""
        with cls._lock:
            cls._cache.clear()


# Compatibility function - maintains original interface
def getGenerator(emulator: str) -> "Generator":
    """Return an instance of the appropriate generator class for the specified emulator.

    This is a compatibility wrapper around GeneratorFactory.create().

    Args:
        emulator: The name of the emulator for which to retrieve the generator.

    Returns:
        An instance of the generator class corresponding to the emulator.

    Raises:
        GeneratorNotFoundError: If no generator is found for the specified emulator.

    """
    return GeneratorFactory.create(emulator)


# Auto-preload on module load for resource-constrained systems
def _auto_preload() -> None:
    """Automatically determine if we should preload common generators based on system resources."""
    try:
        # Check if we're likely on a low-memory system by checking total RAM
        with pathlib.Path("/proc/meminfo").open() as f:
            for line in f:
                if line.startswith("MemTotal:"):
                    total_memory_kb = int(line.split()[1])
                    # Pi Zero typically has ~512MB RAM, use 700MB as threshold
                    if total_memory_kb < 700 * 1024:  # Less than 700MB
                        GeneratorFactory.preload()
                    break
    except (FileNotFoundError, ValueError, IndexError):
        # If we can't determine memory, skip preloading
        pass


# Auto-detect and preload if needed
_auto_preload()
