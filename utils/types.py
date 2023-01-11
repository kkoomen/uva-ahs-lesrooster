"""
This file contains all the custom types that are used throughout the project.
"""

from typing import Literal
from entities.event import Event

Weekday = Literal[1, 2, 3, 4, 5] # 1-5 indicates mon-fri
TimetableList = list[list[Event]]
EventType = Literal['hc', 'wc', 'pr']
Timeslot = Literal[9, 11, 13, 15, 17]
