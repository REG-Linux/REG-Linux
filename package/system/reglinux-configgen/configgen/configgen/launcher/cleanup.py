"""Cleanup manager for REG-Linux ConfigGen.

This module handles cleanup of resources after emulator execution.
"""

from subprocess import Popen
from typing import Any

from configgen.utils.logger import get_logger

eslog = get_logger(__name__)


class CleanupManager:
    """Manages resource cleanup after emulator execution.

    This class tracks resources that need cleanup (mount points, processes,
    compositor state) and ensures they are properly cleaned up.
    """

    def __init__(self) -> None:
        """Initialize the cleanup manager."""
        self.mount_points: list[str] = []
        self.processes: list[Popen] = []
        self.wheel_processes: list[Any] = []
        self.compositor_started = False
        self.evmapy_started = False
        self.rom_mounted = False
        self.rommountpoint: str | None = None
        self.need_end = False

    def register_mount(self, path: str) -> None:
        """Register a mount point for later cleanup.

        Args:
            path: The mount point path.

        """
        self.mount_points.append(path)

    def register_process(self, proc: Popen) -> None:
        """Register a process for later cleanup.

        Args:
            proc: The process to track.

        """
        self.processes.append(proc)

    def register_wheel_process(self, proc: Any) -> None:
        """Register a wheel calibration process for later cleanup.

        Args:
            proc: The wheel process to track.

        """
        self.wheel_processes.append(proc)

    def mark_rom_mounted(self, need_end: bool, rommountpoint: str | None) -> None:
        """Mark that a ROM archive was mounted and needs cleanup.

        Args:
            need_end: Whether zar_end/squashfs_end needs to be called.
            rommountpoint: The mount point path.

        """
        self.rom_mounted = True
        self.need_end = need_end
        self.rommountpoint = rommountpoint

    def mark_compositor_started(self) -> None:
        """Mark that the compositor was started and needs cleanup."""
        self.compositor_started = True

    def mark_evmapy_started(self) -> None:
        """Mark that evmapy was started and needs cleanup."""
        self.evmapy_started = True

    async def cleanup_all(
        self,
        generator: Any | None = None,
        system: Any | None = None,
    ) -> None:
        """Clean up all registered resources.

        Args:
            generator: Optional generator object for compositor cleanup.
            system: Optional system object for compositor cleanup.

        """
        await self._stop_processes()
        await self._cleanup_wheel_processes()
        await self._unmount_rom()
        await self._stop_compositor(generator, system)
        await self._cleanup_evmapy()

    async def _stop_processes(self) -> None:
        """Stop all registered processes."""
        for proc in self.processes:
            try:
                if proc.poll() is None:  # Process still running
                    proc.terminate()
                    try:
                        proc.wait(timeout=2)
                    except Exception:
                        proc.kill()
            except Exception as e:
                eslog.warning(f"Error stopping process: {e}")

    async def _cleanup_wheel_processes(self) -> None:
        """Clean up wheel calibration processes."""
        from configgen.controllers.utils.wheelsUtils import reset_controllers

        if self.wheel_processes:
            eslog.info("Cleaning up wheel processes")
            reset_controllers(self.wheel_processes)

    async def _unmount_rom(self) -> None:
        """Unmount ROM archive if it was mounted."""
        if self.rom_mounted and self.need_end and self.rommountpoint:
            try:
                from configgen.archives import zar

                zar.zar_end(self.rommountpoint)
                eslog.debug(f"Unmounted ROM from {self.rommountpoint}")
            except Exception as e:
                eslog.error(f"Error unmounting ROM: {e}")

    async def _stop_compositor(
        self,
        generator: Any | None = None,
        system: Any | None = None,
    ) -> None:
        """Stop compositor if it was started."""
        if self.compositor_started and generator and system:
            try:
                from configgen.video import windows_manager

                windows_manager.stop_compositor(generator, system)
                eslog.debug("Compositor stopped")
            except Exception as e:
                eslog.warning(f"Error stopping compositor: {e}")

    async def _cleanup_evmapy(self) -> None:
        """Clean up evmapy if it was started."""
        if self.evmapy_started:
            try:
                from configgen.controllers import Evmapy

                Evmapy.stop()
                eslog.debug("Evmapy stopped")
            except Exception as e:
                eslog.warning(f"Error stopping evmapy: {e}")


# Global cleanup manager instance
_cleanup_manager: CleanupManager | None = None


def get_cleanup_manager() -> CleanupManager:
    """Get the global cleanup manager instance.

    Returns:
        The global cleanup manager.

    """
    global _cleanup_manager
    if _cleanup_manager is None:
        _cleanup_manager = CleanupManager()
    return _cleanup_manager


def reset_cleanup_manager() -> None:
    """Reset the global cleanup manager. Useful for testing."""
    global _cleanup_manager
    _cleanup_manager = CleanupManager()
