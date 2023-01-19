from typing import Union

from code.entities.course import Course
from code.entities.room import Room
from code.entities.student import Student
from code.utils.enums import EventType, Weekdays
from code.utils.helpers import make_id


class Event:
    """
    A timetable event which can be added to the timetable.
    """

    def __init__(self,
                 title: str,
                 event_type: EventType,
                 course: Course,
                 weekday: Union[None, int]=None,
                 timeslot: Union[None, int]=None,
                 room: Union[None, Room]=None,
                 students: Union[None, list[Student]]=None) -> None:
        self.id = make_id()
        self.title = title
        self.type = event_type
        self.course = course
        self.weekday = weekday
        self.timeslot = timeslot
        self.room = room
        self.students = students if students is not None else []

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(title:{self.title}, type:{self.type}, timeslot:{self.timeslot}, course:{self.course.name}, room:{self.room}, weekday:{self.weekday})'

    def __lt__(self, other) -> bool:
        """
        Implement the < operator.
        """
        return self.timeslot < other.timeslot

    def assign_students(self, students: list[Student]) -> None:
        """
        Assign new students to the event.
        """
        self.students = students

    def set_room(self, room: Room) -> None:
        """
        Book this timeslot in a certain room.
        """
        self.room = room

    def set_timeslot(self, timeslot: int) -> None:
        """
        Assign this timeslot to a timeslot for the current weekday.
        """
        self.timeslot = timeslot

    def set_weekday(self, weekday: int) -> None:
        """
        Assign this timeslot to a weekday.
        """
        self.weekday = weekday

    def get_formatted_weekday(self) -> str:
        """
        Get the formatted weekday value, i.e. 'mon', 'tue', etc.
        """
        return Weekdays(self.weekday).value

    def get_capacity(self) -> int:
        """
        Get the capacity for this event based on the course.
        """
        return self.course.get_capacity_for_type(self.type)
