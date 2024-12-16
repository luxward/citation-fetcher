import logging
import os

import colorlog

DEFAULT_FORMAT = '%(log_color)s%(asctime)s [%(levelname)s] %(message)s'
if os.environ.get("DEBUG") == "1":
    DEFAULT_FORMAT = '%(log_color)s%(asctime)s %(pathname)s %(lineno)d [%(levelname)s] %(message)s'


def get_default_formatter(no_color=False):
    return colorlog.ColoredFormatter(DEFAULT_FORMAT, no_color=no_color, log_colors={
        **colorlog.default_log_colors,
        'TEXT': 'white',
        'DEBUG': 'cyan'})


def create_logger(logger_name: str, stream_level=logging.INFO) -> logging.Logger:
    logger = colorlog.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    logger.handlers.clear()

    streamHandler = colorlog.StreamHandler()
    streamHandler.setLevel(stream_level)
    streamHandler.setFormatter(get_default_formatter())
    logger.addHandler(streamHandler)
    return logger
