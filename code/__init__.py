from datetime import datetime
import logging
import os

from code.utils.constants import LOG_DIR, OUT_DIR

# ==============================================================================
# Create some necessary directories if they don't exist yet.
# ==============================================================================
dirs = [OUT_DIR, LOG_DIR]
for d in dirs:
    if not os.path.isdir(d):
        os.mkdir(d)

# ==============================================================================
# Create logger
# ==============================================================================
logger_names = ['global', __name__]
for logger_name in logger_names:
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)


    today_date = str(datetime.now().date())
    handlers = [
        logging.StreamHandler(),
        logging.FileHandler(f'{LOG_DIR}/{today_date}.txt')
    ]

    for handler in handlers:
        handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')
        handler.setFormatter(formatter)

        logger.addHandler(handler)

# Immediately log as an indication that the program has initialized.
global_logger = logging.getLogger('global')
global_logger.info('='*80)
global_logger.info(f'Program started at {str(datetime.now())}')
global_logger.info('='*80)
