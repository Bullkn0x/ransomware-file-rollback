import logging 


class Logger:
    """
    A class for creating logger instances.

    Attributes:
    - name (str): The name of the logger instance.
    - level (int): The logging level for the logger instance.

    Methods:
    - get_logger(): Returns the logger instance.
    - get_error_logger(): Returns the error logger instance.
    """
    def __init__(self, name, level=logging.INFO):
        # Create a logger instance with the provided name and logging level
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # Set up formatter for log messages
        formatter = logging.Formatter('%(levelname)s:%(name)s:%(funcName)s:%(message)s')

        # Set up file handler for writing log messages to a file
        file_handler = logging.FileHandler(f'logs/{name}.log')
        file_handler.setFormatter(formatter)

        # Set up stream handler for writing log messages to the console
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)

        # Add the file handler and stream handler to the logger instance
        self.logger.addHandler(file_handler)
        self.logger.addHandler(stream_handler)

        # Set up an error logger instance
        self.error_logger = logging.getLogger(f'{name}_errors')
        self.error_logger.setLevel(logging.ERROR)

        # Set up formatter for error messages
        error_formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')

        # Set up file handler for writing error messages to a file
        error_file_handler = logging.FileHandler(f'logs/{name}_errors.log')
        error_file_handler.setFormatter(error_formatter)
        
        # Add the file handler to the error logger instance
        self.error_logger.addHandler(error_file_handler)


    def get_logger(self):
        return self.logger

    def get_error_logger(self):
        return self.error_logger
