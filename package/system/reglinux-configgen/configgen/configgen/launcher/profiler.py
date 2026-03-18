"""Profiler for REG-Linux ConfigGen.

This module handles profiling for performance analysis of the emulator launcher.
"""

import cProfile
import pstats

from configgen.config.paths import EMULATORLAUNCHER_PERF, EMULATORLAUNCHER_PROF


class Profiler:
    """Manages profiling for performance analysis.

    Usage:
        profiler = Profiler(enabled=True)
        profiler.start()
        # ... code to profile ...
        profiler.stop()
        profiler.dump_stats()

    """

    def __init__(self, enabled: bool = False):
        """Initialize the profiler.

        Args:
            enabled: Whether profiling is enabled.

        """
        self.enabled = enabled
        self.profiler: cProfile.Profile | None = None

    def start(self) -> None:
        """Start profiling if enabled."""
        if self.enabled and not EMULATORLAUNCHER_PERF.exists():
            self.enabled = False

        if self.enabled:
            self.profiler = cProfile.Profile()
            try:
                self.profiler.enable()
            except ValueError:
                # Another profiling tool is already active
                self.enabled = False
                self.profiler = None

    def stop(self) -> None:
        """Stop profiling and dump stats if enabled."""
        if self.profiler:
            self.profiler.disable()
            self.profiler.dump_stats(str(EMULATORLAUNCHER_PROF))

    def get_stats(self) -> pstats.Stats | None:
        """Get profiling statistics.

        Returns:
            pstats.Stats object if profiling was enabled, None otherwise.

        """
        if self.profiler and EMULATORLAUNCHER_PROF.exists():
            return pstats.Stats(str(EMULATORLAUNCHER_PROF))
        return None

    def print_stats(self, sort_by: str = "cumulative", top_n: int = 10) -> None:
        """Print profiling statistics.

        Args:
            sort_by: Sort criterion for stats.
            top_n: Number of top functions to display.

        """
        stats = self.get_stats()
        if stats:
            stats.sort_stats(sort_by)
            stats.print_stats(top_n)


def is_profiling_enabled() -> bool:
    """Check if profiling is enabled based on marker file.

    Returns:
        True if EMULATORLAUNCHER_PERF marker file exists.

    """
    return EMULATORLAUNCHER_PERF.exists()
