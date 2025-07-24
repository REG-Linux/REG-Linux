#!/usr/bin/env python3

import logging
import sys

class MaxLevelFilter(logging.Filter):
    def __init__(self, max_level: int):
        super().__init__()
        self.max_level = max_level

    def filter(self, record):
        return record.levelno < self.max_level

def get_logger(module_name: str, level: int = logging.DEBUG,
               fmt: str = "%(asctime)s %(levelname)s (%(filename)s:%(lineno)d):%(funcName)s %(message)s"
              ) -> logging.Logger:
    error_level = logging.WARNING
    formatter = logging.Formatter(fmt)

    stdout = logging.StreamHandler(sys.stdout)
    stdout.setFormatter(formatter)
    stdout.setLevel(logging.DEBUG)
    stdout.addFilter(MaxLevelFilter(error_level))

    stderr = logging.StreamHandler(sys.stderr)
    stderr.setFormatter(formatter)
    stderr.setLevel(error_level)

    logger = logging.getLogger(module_name)
    logger.setLevel(level)

    if logger.hasHandlers():
        logger.handlers.clear()

    logger.addHandler(stdout)
    logger.addHandler(stderr)

    return logger
