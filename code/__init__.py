import os

from code.utils.constants import LOG_DIR, OUT_DIR

# Create some necessary directories if they don't exist yet.
dirs = [OUT_DIR, LOG_DIR]
for d in dirs:
    if not os.path.isdir(d):
        os.mkdir(d)
