import random
from typing import Union

from code.entities.course import Course
from code.entities.room import Room
from code.entities.student import Student


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
                 weekday: int,
                 students: Union[None, list[Student]] = None) -> None:
        self.id = random.getrandbits(32)
        self.title = title
        self.type = event_type
        self.timeslot = timeslot
        self.course = course
        self.room = room
        self.weekday = weekday
        self.students = students if students is not None else []

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(title:{self.title}, type:{self.type}, timeslot:{self.timeslot}, course:{self.course.name}, room:{self.room}, weekday:{self.weekday})'

    def assign_students(self, students: list[Student]) -> None:
        """
        Assign new students to the event.
        """
        self.students = students

    def set_timeslot(self, timeslot: int) -> None:
        """
        Set a new timeslot value.
        """
        self.timeslot = timeslot

    def set_weekday(self, weekday: int) -> None:
        """
        Set a new weekday value.
        """
        self.weekday = weekday
