"""
This file contains helper functions that are used throughout the project.
"""

import os

from utils.constants import ASSETS_DIR


def asset_path(filename: str) -> str:
    return os.path.join(ASSETS_DIR, filename)
