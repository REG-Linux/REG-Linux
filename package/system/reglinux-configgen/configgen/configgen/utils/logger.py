import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any


class MaxLevelFilter(logging.Filter):
    def __init__(self, max_level: int):
        super().__init__()
        self.max_level = max_level

    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno < self.max_level


class BrokenPipeHandler(logging.Handler):
    """Custom handler that gracefully handles BrokenPipeError when writing to stdout/stderr."""

    def __init__(self, stream):
        super().__init__()
        self.stream = stream
        self.terminator = "\n"

    def emit(self, record):
        try:
            msg = self.format(record)
            stream = self.stream
            stream.write(msg + self.terminator)
            self.flush()
        except BrokenPipeError:
            # Gracefully handle broken pipe by redirecting to devnull
            devnull = os.open(os.devnull, os.O_WRONLY)
            os.dup2(
                devnull, self.stream.fileno(),
            )  # Replace the broken pipe with devnull
            os.close(devnull)
        except Exception:
            self.handleError(record)


class LoggerManager:
    """Enhanced logger manager with additional configuration options."""

    _instances = {}

    def __new__(cls, module_name: str) -> "LoggerManager":
        if module_name not in cls._instances:
            cls._instances[module_name] = super().__new__(cls)
        return cls._instances[module_name]

    def __init__(self, module_name: str) -> None:
        self.module_name = module_name
        self.logger = logging.getLogger(module_name)
        # Prevent duplicate initialization
        if hasattr(self, "_initialized"):
            return
        self._initialized = True

    def setup_logger(
        self,
        level: int = logging.DEBUG,
        fmt: str = "%(asctime)s %(levelname)s (%(filename)s:%(lineno)d):%(funcName)s %(message)s",
        enable_file_logging: bool = False,
        log_file_path: str | None = None,
        max_file_size: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 3,
        enable_stdout: bool = True,
        enable_stderr: bool = True,
    ) -> logging.Logger:
        """Set up logger with various configuration options.

        Args:
            level: Logging level (default: DEBUG)
            fmt: Log format string
            enable_file_logging: Enable logging to file
            log_file_path: Path to log file (default: /tmp/module_name.log)
            max_file_size: Maximum file size before rotation (in bytes)
            backup_count: Number of backup files to keep
            enable_stdout: Enable stdout handler
            enable_stderr: Enable stderr handler

        """
        formatter = logging.Formatter(fmt)

        # Clear existing handlers to prevent duplicates
        if self.logger.hasHandlers():
            self.logger.handlers.clear()

        self.logger.setLevel(level)

        # Setup stdout handler for lower level logs
        if enable_stdout:
            error_level = logging.WARNING
            stdout_handler = BrokenPipeHandler(sys.stdout)
            stdout_handler.setFormatter(formatter)
            stdout_handler.setLevel(logging.DEBUG)
            stdout_handler.addFilter(MaxLevelFilter(error_level))
            self.logger.addHandler(stdout_handler)

        # Setup stderr handler for error logs
        if enable_stderr:
            stderr_handler = BrokenPipeHandler(sys.stderr)
            stderr_handler.setFormatter(formatter)
            stderr_handler.setLevel(logging.WARNING)
            self.logger.addHandler(stderr_handler)

        # Setup file handler with rotation
        if enable_file_logging:
            if not log_file_path:
                log_file_path = f"/tmp/{self.module_name}.log"

            # Create directory if it doesn't exist
            log_dir = Path(log_file_path).parent
            if log_dir and not log_dir.exists():
                log_dir.mkdir(parents=True, exist_ok=True)

            file_handler = RotatingFileHandler(
                log_file_path,
                maxBytes=max_file_size,
                backupCount=backup_count,
            )
            file_handler.setFormatter(formatter)
            file_handler.setLevel(level)
            self.logger.addHandler(file_handler)

        return self.logger


def get_logger(
    module_name: str,
    level: int = logging.DEBUG,
    fmt: str = "%(asctime)s %(levelname)s (%(filename)s:%(lineno)d):%(funcName)s %(message)s",
    enable_file_logging: bool = False,
    log_file_path: str | None = None,
    max_file_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 3,
    enable_stdout: bool = True,
    enable_stderr: bool = True,
) -> logging.Logger:
    """Get a configured logger instance.

    Args:
        module_name: Name of the module requesting the logger
        level: Logging level (default: DEBUG)
        fmt: Log format string
        enable_file_logging: Enable logging to file
        log_file_path: Path to log file (default: /tmp/module_name.log)
        max_file_size: Maximum file size before rotation (in bytes)
        backup_count: Number of backup files to keep
        enable_stdout: Enable stdout handler
        enable_stderr: Enable stderr handler

    Returns:
        Configured logger instance

    """
    logger_manager = LoggerManager(module_name)
    return logger_manager.setup_logger(
        level=level,
        fmt=fmt,
        enable_file_logging=enable_file_logging,
        log_file_path=log_file_path,
        max_file_size=max_file_size,
        backup_count=backup_count,
        enable_stdout=enable_stdout,
        enable_stderr=enable_stderr,
    )


def set_global_log_level(level: int):
    """Set the global log level for all loggers.

    Args:
        level: Logging level to set globally

    """
    logging.getLogger().setLevel(level)


def add_log_context(logger: logging.Logger, **context: Any):
    """Add contextual information to a logger.

    Args:
        logger: Base logger to add context to
        **context: Context key-value pairs

    Returns:
        LoggerAdapter with context

    """
    return logging.LoggerAdapter(logger, context)
