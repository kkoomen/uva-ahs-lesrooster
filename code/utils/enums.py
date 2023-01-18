"""
This file contains enums that are used throughout the project.
"""

from enum import Enum


Weekdays = Enum('Weekdays', ['mon', 'tue', 'wed', 'thu', 'fri'])

class EventType(Enum):
    LECTURE = 'hc'
    SEMINAR = 'wc'
    PRACTICUM = 'pr'
