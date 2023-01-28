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
        return f'{self.__class__.__name__}(id:{self.id}, title:{self.title}, type:{self.type}, timeslot:{self.timeslot}, course:{self.course.name}, room:{self.room}, weekday:{self.weekday})'

    def __lt__(self, other) -> bool:
        """
        Implement the < operator.
        """
        assert self.room is not None, 'room must not be None'
        assert other.room is not None, 'other room must not be None'

        return self.weekday < other.weekday or \
            self.weekday == other.weekday and (
                self.timeslot < other.timeslot or \
                self.timeslot == other.timeslot and self.room.capacity < other.room.capacity
            )

    def __eq__(self, other) -> bool:
        """
        Check if two events are of the same class type and have the same values.
        """
        return self.__class__ == other.__class__ and \
            self.type == other.type and \
            self.room == other.room and \
            self.weekday == other.weekday and \
            self.timeslot == other.timeslot and \
            self.course == other.course and \
            self.title == other.title and \
            sorted(self.students) == sorted(other.students)

    def add_student(self, student: Student) -> None:
        """
        Assign a single student to the event.
        """
        self.students.append(student)

    def serialize(self) -> dict:
        """
        Serialize the data inside this class to a JSON-friendly structure.
        """
        return {
            'id': self.id,
            'title': self.title,
            'type': self.type.value,
            'course': self.course.name,
            'weekday': self.weekday,
            'timeslot': self.timeslot,
            'room': str(self.room),
        }

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
        return Weekdays(self.weekday).name

    def get_capacity(self) -> int:
        """
        Get the capacity for this event based on the course.
        """
        return self.course.get_capacity_for_type(self.type)
