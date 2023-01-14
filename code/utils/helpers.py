"""
This file contains helper functions that are used throughout the project.
"""

import copy
import os
import random

from code.utils.constants import DATA_DIR


def data_path(filename: str) -> str:
    """
    Get the absolute filepath for a certain data file.
    """
    return os.path.join(DATA_DIR, filename)


def split_list_random(items: list, k: int) -> list[list]:
    """
    Split a list with items into random groups of amount `k`.

    >>> random.seed(0)
    >>> split_list_random(['a', 'b', 'c', 'd', 'e'], 2)
    [['b', 'c'], ['a', 'e'], ['d']]
    """
    choices = copy.deepcopy(items)
    groups = []
    total_groups = k + 1

    for _ in range(total_groups):
        group = []

        for _ in range(k):
            if len(choices) > 0:
                random_index = random.randrange(min(len(choices), k))
                item = choices.pop(random_index)
                group.append(item)

        groups.append(group)

    return groups
