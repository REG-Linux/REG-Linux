#!/usr/bin/env python3

import logging
import sys

def get_logger(module_name: str, level: int = logging.DEBUG) -> logging.Logger:
    error_level = logging.WARNING
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s (%(filename)s:%(lineno)d):%(funcName)s %(message)s"
    )
    stdout = logging.StreamHandler(sys.stdout)
    stdout.setFormatter(formatter)
    stdout.setLevel(logging.DEBUG)
    stdout.addFilter(lambda record: record.levelno < error_level)

    stderr = logging.StreamHandler(sys.stderr)
    stderr.setFormatter(formatter)
    stderr.setLevel(error_level)

    logger = logging.getLogger(module_name)
    logger.setLevel(level)

    if not logger.handlers:  # evita múltiplos handlers duplicados
        logger.addHandler(stdout)
        logger.addHandler(stderr)

    return logger
