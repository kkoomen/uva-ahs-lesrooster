"""
This file contains helper functions that are used throughout the project.
"""

import copy
from datetime import datetime
import math
import os
import random
from typing import Any
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
    """
    groups = []
    total_groups = math.ceil(len(items) / k)

    for i in range(total_groups):
        start = k * i
        end = start + k
        group = items[start:end]
        groups.append(group)

    return groups


def split_list_random(items: list, k: int) -> list[list]:
    """
    Split a list with items into random groups of size `k`.
    """
    choices = copy.deepcopy(items)
    groups = []
    total_groups = math.ceil(len(items) / k)

    for _ in range(total_groups):
        group = []

        for _ in range(k):
            if len(choices) > 0:
                random_index = random.randrange(len(choices))
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


def serialize(obj: Any) -> Any:
    """
    Serialize all classes inside a dictionary or list or the class itself.

    Each class can implement their custom `serialize` method in order to decide
    what to return for that specific class when being serialized.
    """
    if isinstance(obj, list):
        for i, item in enumerate(obj):
            obj[i] = serialize(item)
    elif isinstance(obj, dict):
        for key, value in obj.items():
            obj[key] = serialize(value)
    elif hasattr(obj, 'serialize'):
        obj = serialize(obj.serialize())
    return obj
