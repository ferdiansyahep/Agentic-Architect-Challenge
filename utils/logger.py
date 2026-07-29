import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path


def _build_handler(level, formatter):
    handler = logging.StreamHandler()
    handler.setLevel(level)
    handler.setFormatter(formatter)
    return handler


def get_logger(name):
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    log_level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_name, logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    logger.setLevel(log_level)
    logger.propagate = False
    logger.addHandler(_build_handler(log_level, formatter))

    log_file = os.getenv("LOG_FILE", "logs/app.log")
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=1_000_000,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger