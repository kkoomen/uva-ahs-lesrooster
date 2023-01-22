"""
This file contains custom decorators that can be used throughout the project.
"""

import timeit
import logging

logger = logging.getLogger(__name__)


def timer(func):
    """
    Calculate the execution time of a function.
    """
    def wrapper(*args, **kwargs):
        start_time = timeit.default_timer()
        result = func(*args, **kwargs)
        end_time = timeit.default_timer()
        exec_time = end_time - start_time
        logger.debug(f'{func.__qualname__}() executed in {exec_time:.8f} seconds')
        return result
    return wrapper
