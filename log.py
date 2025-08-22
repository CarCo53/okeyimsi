import logging
from functools import wraps

class CentralLogger:
    def __init__(self, name="okey_logger", log_file="game.log"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)
        # File handler
        fh = logging.FileHandler(log_file, encoding='utf-8')
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)

        if not self.logger.handlers:
            self.logger.addHandler(ch)
            self.logger.addHandler(fh)

    def info(self, msg):
        self.logger.info(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)

    def debug(self, msg):
        self.logger.debug(msg)

    def log_function(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            self.logger.info(f"CALL {func.__qualname__} args={args} kwargs={kwargs}")
            try:
                result = func(*args, **kwargs)
                self.logger.info(f"RETURN {func.__qualname__} result={result}")
                return result
            except Exception as e:
                self.logger.error(f"ERROR in {func.__qualname__}: {e}", exc_info=True)
                raise
        return wrapper

logger = CentralLogger()