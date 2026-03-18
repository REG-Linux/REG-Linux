"""Custom exceptions for REG-Linux ConfigGen.

This module defines a hierarchy of custom exceptions for better error handling
and more informative error messages throughout the configgen package.
"""


class ConfigGenError(Exception):
    """Base exception for all ConfigGen errors.

    All custom exceptions in this module inherit from ConfigGenError to allow
    catching all configgen-related errors with a single exception type.
    """

    def __init__(self, message: str) -> None:
        """Initialize ConfigGenError with a descriptive message.

        Args:
            message: A descriptive error message explaining what went wrong.

        """
        super().__init__(message)
        self.message = message


class EmulatorNotFoundError(ConfigGenError):
    """Raised when no emulator configuration is found for a system."""

    def __init__(self, system: str | None = None) -> None:
        """Initialize EmulatorNotFoundError.

        Args:
            system: The name of the system for which no emulator was found.

        """
        message = (
            f"No emulator found for system '{system}'"
            if system
            else "No emulator found"
        )
        super().__init__(message)
        self.system = system


class ArchiveMountError(ConfigGenError):
    """Raised when mounting or unmounting an archive fails."""

    def __init__(self, archive_path: str, operation: str = "mount") -> None:
        """Initialize ArchiveMountError.

        Args:
            archive_path: Path to the archive file or mount point.
            operation: The operation that failed ('mount' or 'unmount').

        """
        if operation == "mount":
            message = f"Unable to mount the archive: {archive_path}"
        else:
            message = f"Unable to unmount the archive: {archive_path}"
        super().__init__(message)
        self.archive_path = archive_path
        self.operation = operation


class BIOSNotFoundError(ConfigGenError):
    """Raised when a required BIOS file is not found."""

    def __init__(self, emulator: str, bios_name: str | None = None) -> None:
        """Initialize BIOSNotFoundError.

        Args:
            emulator: The name of the emulator requiring the BIOS.
            bios_name: Optional specific BIOS file name that was not found.

        """
        if bios_name:
            message = f"No {bios_name} BIOS found for {emulator}"
        else:
            message = f"No BIOS found for {emulator}"
        super().__init__(message)
        self.emulator = emulator
        self.bios_name = bios_name


class MachineNotFoundError(ConfigGenError):
    """Raised when a machine configuration is not found."""

    def __init__(self, machine: str, emulator: str) -> None:
        """Initialize MachineNotFoundError.

        Args:
            machine: The name of the machine configuration.
            emulator: The emulator requiring the machine configuration.

        """
        message = f"No BIOS found for machine '{machine}' on {emulator}"
        super().__init__(message)
        self.machine = machine
        self.emulator = emulator


class GeneratorError(ConfigGenError):
    """Raised when a generator encounters an error during configuration."""

    def __init__(self, emulator: str, message: str) -> None:
        """Initialize GeneratorError.

        Args:
            emulator: The name of the emulator being configured.
            message: A descriptive error message.

        """
        full_message = f"Error configuring {emulator}: {message}"
        super().__init__(full_message)
        self.emulator = emulator


class FileMissingError(ConfigGenError):
    """Raised when a required file is missing."""

    def __init__(self, file_path: str, context: str | None = None) -> None:
        """Initialize FileMissingError.

        Args:
            file_path: Path to the missing file.
            context: Optional context about why the file is needed.

        """
        if context:
            message = f"Missing required file '{file_path}': {context}"
        else:
            message = f"Missing required file: {file_path}"
        super().__init__(message)
        self.file_path = file_path


class ImageProcessingError(ConfigGenError):
    """Raised when image processing operations fail."""

    def __init__(self, operation: str, details: str | None = None) -> None:
        """Initialize ImageProcessingError.

        Args:
            operation: The image processing operation that failed.
            details: Optional additional details about the failure.

        """
        message = f"Image processing error during {operation}"
        if details:
            message += f": {details}"
        super().__init__(message)
        self.operation = operation


class TattooImageError(ImageProcessingError):
    """Raised when tattoo image processing fails."""

    def __init__(self, reason: str) -> None:
        """Initialize TattooImageError.

        Args:
            reason: Description of why the tattoo image could not be processed.

        """
        super().__init__("tattoo processing", reason)
        self.reason = reason


class BezelImageError(ImageProcessingError):
    """Raised when bezel image processing fails."""

    def __init__(self, reason: str) -> None:
        """Initialize BezelImageError.

        Args:
            reason: Description of why the bezel image could not be processed.

        """
        super().__init__("bezel processing", reason)
        self.reason = reason


class ExternalScriptError(ConfigGenError):
    """Raised when an external script returns an error."""

    def __init__(self, script_path: str, message: str) -> None:
        """Initialize ExternalScriptError.

        Args:
            script_path: Path to the script that failed.
            message: Error message from the script.

        """
        super().__init__(f"External script error in '{script_path}': {message}")
        self.script_path = script_path
