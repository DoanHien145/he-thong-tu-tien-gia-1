import logging
import sys
import os

def setup_logger():
    """
    Sets up custom logger for the Discord Bot.
    Outputs to stdout and appends to bot.log.
    """
    logger = logging.getLogger("TôngMônBot")
    logger.setLevel(logging.INFO)

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Stream Handler (Console output)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File Handler
    try:
        os.makedirs("logs", exist_ok=True)
        file_handler = logging.FileHandler("logs/bot.log", encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"Could not setup file logger: {e}")

    return logger

logger = setup_logger()
