"""
This file contains all the custom types that are used throughout the project.
"""


from typing import Literal
from entities.event import Event


Weekday = Literal[1, 2, 3, 4, 5] # 1-5 indicates mon-fri
TimetableList = list[list[Event]]
EventType = Literal['hc', 'wc', 'pr']
Timeslot = Literal[9, 11, 13, 15, 17]
RoomId = Literal[
    'A1.04',
    'A1.06',
    'A1.08',
    'A1.10',
    'B0.201',
    'C0.110',
    'C1.112',
]
