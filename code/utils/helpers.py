"""
This file contains helper functions that are used throughout the project.
"""

import os

from code.utils.constants import DATA_DIR


def data_path(filename: str) -> str:
    return os.path.join(DATA_DIR, filename)
