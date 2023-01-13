import random

from code.entities.course import Course
from code.entities.room import Room


class Event:
    """
    A timetable event which can be added to the timetable.
    """

    def __init__(self,
                 title: str,
                 event_type: str,
                 timeslot: int,
                 course: Course,
                 room: Room,
                 weekday: int) -> None:
        self.id = random.getrandbits(32)
        self.title = title
        self.type = event_type
        self.timeslot = timeslot
        self.course = course
        self.room = room
        self.weekday = weekday

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(title:{self.title}, type:{self.type}, timeslot:{self.timeslot}, course:{self.course.name}, room:{self.room}, weekday:{self.weekday})'
