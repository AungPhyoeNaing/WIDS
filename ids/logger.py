import logging
from logging.handlers import RotatingFileHandler
import os

class IDSLogger:
    def __init__(self, name="WIDS"):
        self.logger = logging.getLogger(name)
        if not self.logger.handlers:
            # Console handler
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(
                "%(asctime)s [%(name)s] %(levelname)s: %(message)s",
                datefmt="%H:%M:%S"
            ))
            self.logger.addHandler(handler)
            
            # File handler with rotation (5MB max, 3 backups)
            try:
                log_dir = os.path.join(os.path.dirname(__file__), "..", "logs")
                os.makedirs(log_dir, exist_ok=True)
                file_handler = RotatingFileHandler(
                    os.path.join(log_dir, "wids.log"),
                    maxBytes=5*1024*1024,  # 5MB
                    backupCount=3
                )
                file_handler.setFormatter(logging.Formatter(
                    "%(asctime)s [%(name)s] %(levelname)s: %(message)s"
                ))
                self.logger.addHandler(file_handler)
            except Exception:
                pass  # File logging is optional
            
            self.logger.setLevel(logging.WARNING)

    def warning(self, message):
        self.logger.warning(message)

    def info(self, message):
        self.logger.info(message)

    def error(self, message):
        self.logger.error(message)
