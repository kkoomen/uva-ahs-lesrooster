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
                 room: Room,
                 weekday: int,
                 enrolled_students: list[Student] = []) -> None:
        self.title = title
        self.type = event_type
        self.timeslot = timeslot
        self.room = room
        self.weekday = weekday
        self.enrolled_students = enrolled_students

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(title:{self.title}, type:{self.type}, timeslot:{self.timeslot}, room:{self.room}, weekday:{self.weekday}, enrolled_students:{self.enrolled_students})'
