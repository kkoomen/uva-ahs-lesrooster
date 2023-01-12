"""
This file contains constants that are used throughout the project.
"""

import os

ROOT_DIR = os.path.realpath(os.path.join(os.path.basename(__file__), '../'))
DATA_DIR = os.path.join(ROOT_DIR, 'data')
OUT_DIR = os.path.join(ROOT_DIR, 'out')

WEEKDAYS = ['mon', 'tue', 'wed', 'thu', 'fri']
