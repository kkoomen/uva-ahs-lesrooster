from entities.lecture_room import LectureRoom
from utils.types import EventType, Timeslot, Weekday


class Event:
    """
    A timetable event which can be added to the timetable.
    """

    def __init__(self,
                 event_type: EventType,
                 timeslot: Timeslot,
                 room: LectureRoom,
                 weekday: Weekday,
                 student_numbers: list[str] = []) -> None:
        self.type = event_type
        self.timeslot = timeslot
        self.room = room
        self.weekday = weekday
        self.student_numbers = student_numbers

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(type:{self.type}, timeslot:{self.timeslot}, room:{self.room}, weekday:{self.weekday}, student_numbers:{self.student_numbers})'
