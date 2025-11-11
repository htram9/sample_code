# Provide a logger wrapper that timestamps the way I specify
#
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional
from logging.handlers import RotatingFileHandler


class SimpleLogger:
    """A simple logging class with file and console output support."""
    
    # Class-level constants
    MAX_BYTES = 1024 * 1024     # 1MB log file limit
    MAX_BACKUPS = 3             # Only 3 backups kept for log files

    def __init__(
        self,
        name: str = "SimpleLogger",
        log_file: Optional[str] = None,
        level: int = logging.INFO,
        console: bool = True
    ):
        """
        Initialize the logger.
        
        Args:
            name: Logger name
            log_file: Path to log file (optional)
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            console: Whether to output to console
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.handlers.clear()  # Clear existing handlers


        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        
        # Add console handler if requested
        if console:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(level)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
        
        # Add file handler if log_file is specified
        if log_file:
            # Create a RotatingFileHandler
            # Rotates when the file reaches size limit, keeps specified number of backup files
            # 
            Path(log_file).parent.mkdir(parents=True, exist_ok=True)
            handler = RotatingFileHandler(log_file, maxBytes=SimpleLogger.MAX_BYTES, backupCount=SimpleLogger.MAX_BACKUPS)
            handler.setLevel(level)
            handler.setFormatter(formatter)

            self.logger.addHandler(handler)

    def debug(self, message: str):
        """Log a debug message."""
        self.logger.debug(message)
    
    def info(self, message: str):
        """Log an info message."""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Log a warning message."""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Log an error message."""
        self.logger.error(message)
    
    def critical(self, message: str):
        """Log a critical message."""
        self.logger.critical(message)


# Helper functions to verify log rotation

# Searching backwards is more efficient for large files
def get_last_line(logger: SimpleLogger, 
                  file_path: str):
    try:
        with open(file_path, 'rb') as f:
            try:
                f.seek(-2, os.SEEK_END)  # Start from 2 bytes before the end
                while f.read(1) != b'\n':
                    f.seek(-2, os.SEEK_CUR)
            except OSError:  # Handle cases where the file might be very small or have only one line
                f.seek(0)
            last_line = f.readline().decode().strip()
    except FileNotFoundError:
        logger.error(f"Error: The file '{file_path}' was not found.")
    except Exception as e:
        logger.error(f"An error occurred: {e}")

    return last_line

def get_first_line(logger: SimpleLogger,
                   file_path: str):
    try:
        with open(file_path, 'r') as f:
            first_line = f.readline()
    except FileNotFoundError:
        logger.error(f"Error: The file '{file_path}' was not found.")
    except Exception as e:
        logger.error(f"An error occurred: {e}")

    return first_line
    

# Test usage
if __name__ == "__main__":
    # Create logger with both console and file output
    logger = SimpleLogger(
        name="MyApp",
        log_file="logs/myapp.log",
        level=logging.DEBUG
    )
    
    # Log messages at different levels
    logger.debug("This is a debug message")
    logger.info("Application started successfully")
    logger.warning("This is a warning message")
    logger.error("An error occurred")
    logger.critical("Critical system failure")
    
    # Create a console-only logger
    console_logger = SimpleLogger(name="ConsoleOnly", console=True)
    console_logger.info("This only goes to console")
    
    # Create a file-only logger
    filename = "logs/file_only.log"
    file_logger = SimpleLogger(
        name="FileOnly",
        log_file=filename,
        console=False
    )
    file_logger.info("This only goes to the file")

    # Log some messages to demonstrate rotation
    for i in range(100000):
        file_logger.info(f"This is log message number {i}")
    
    # Verify log rotation
    try:
        for i in range(SimpleLogger.MAX_BACKUPS):
            file1 = f"{filename}.{i}"
            file2 = f"{filename}.{i+1}"
            if (i == 0):
                file1 = filename


            last_line = get_last_line(console_logger, file2).strip()
            first_line = get_first_line(console_logger, file1).strip()
            console_logger.info(f"last line [{last_line}]")
            console_logger.info(f"first line [{first_line}]")
            words = last_line.split()
            last_word = words[-1]
            last_id = int(last_word)
            words = first_line.split()
            last_word = words[-1]
            first_id = int(last_word)
            if (first_id == (last_id + 1)):
                console_logger.info(f"Log rotation correct between file [{file2}] and file [{file1}]...")
            else:
                console_logger.error(f"Log rotation INCORRECT between file [{file2}] and file [{file1}]...")

    except Exception as e:
        console_logger.error(f"An error occurred: {e}")

    console_logger.info("Done testing SimpleLogger...")
    