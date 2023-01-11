from entities.room import Room


class Event:
    """
    A timetable event which can be added to the timetable.
    """

    def __init__(self,
                 event_type: str,
                 timeslot: int,
                 room: Room,
                 weekday: int,
                 student_numbers: list[str] = []) -> None:
        self.type = event_type
        self.timeslot = timeslot
        self.room = room
        self.weekday = weekday
        self.student_numbers = student_numbers

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(type:{self.type}, timeslot:{self.timeslot}, room:{self.room}, weekday:{self.weekday}, student_numbers:{self.student_numbers})'
