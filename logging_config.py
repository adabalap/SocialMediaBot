import logging

def setup_logging(log_file, logging_level):
    """
    Sets up the logging configuration.
    """
    level = logging.INFO if logging_level == "INFO" else logging.DEBUG
    logging.basicConfig(
        filename=log_file,
        level=level,
        format='%(asctime)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logging.info("Logging setup complete.")

