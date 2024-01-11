import logging

def configure_logging():
    # Remove existing handlers from the root logger
    root_logger = logging.getLogger()
    for handler in root_logger.handlers:
        root_logger.removeHandler(handler)

    # Set the logging level to INFO for the root logger
    root_logger.setLevel(logging.INFO)

    # Create a FileHandler to log messages to a file
    file_handler = logging.FileHandler('logfile.log')
    file_handler.setLevel(logging.DEBUG)

    # Create a StreamHandler to log messages to the console (stdout)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # Create a formatter for the log messages
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Set the formatter for both handlers
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add both handlers to the root logger
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

# Configure logging
configure_logging()

# Example usage
logging.debug('This is a debug message.')
logging.info('This is an info message.')

