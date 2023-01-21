"""
This file contains helper functions that are used throughout the project.
"""

import copy
from datetime import datetime
import os
import random
from tzlocal import get_localzone

from code.utils.constants import DATA_DIR


def data_path(filename: str) -> str:
    """
    Get the absolute filepath for a certain data file.
    """
    return os.path.join(DATA_DIR, filename)


def split_list(items: list, k: int) -> list[list]:
    """
    Split a list with items into groups of size `k`.

    >>> split_list(['a', 'b', 'c', 'd', 'e'], 2)
    [['a', 'b'], ['c', 'd'], ['e']]
    """
    groups = []
    total_groups = k + 1

    for i in range(total_groups):
        start = k * i
        end = start + k
        group = items[start:end]
        groups.append(group)

    return groups


def split_list_random(items: list, k: int) -> list[list]:
    """
    Split a list with items into random groups of size `k`.

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


def make_id() -> int:
    """
    Create a random id.
    """
    return random.getrandbits(32)


def remove_duplicates(items: list) -> list:
    """
    Remove duplicates in a list.

    >>> remove_duplicates(['a', 'b', 'b', 'c'])
    ['a', 'b', 'c']
    """
    new_list = []

    for item in items:
        if item not in new_list:
            new_list.append(item)

    return new_list


def get_utc_offset() -> str:
    """
    Get the utc offset by automatically detecting the local timezone.
    """
    tz = get_localzone()

    # Returns something like '+0100'
    offset = datetime.now(tz).strftime('%z')

    # Convert '+0100' to '+01:00'
    return f'{offset[:3]}:{offset[3:]}'
