from entities.event import Event
from utils.types import TimetableList


class Timetable:
    """
    A single timetable can contain events that can be added or removed.

    An example timetable structure is described below:
    {
        [ // monday
            Event(type:hc, timeslot:9, room:C0.110, weekday:1, student_numbers:[1,2...]),
            Event(type:hc, timeslot:9, room:C1.04, weekday:1, student_numbers:[1,2...]),
            Event(type:hc, timeslot:11, room:C0.110, weekday:1, student_numbers:[1,2...]),
        ],
        [ // tuesday ],
        [ // wednesday
            Event(type:hc, timeslot:9, room:C1.08, weekday:3, student_numbers:[1,2...]),
        ],
        [ // thursday ],
        [ // friday ],
    }
    """

    def __init__(self) -> None:
        self.timetable: TimetableList = [[], [], [], [], []]

    def add_event(self, event: Event) -> bool:
        """
        Add a single event to the timetable.

        :returns: True if the event has been added, False otherwise.
        """
        self.timetable[event.weekday - 1].append(event)
        return True

    def remove_event(self, event: Event) -> bool:
        """
        Remove a single event from the timetable.

        :returns: True if `event` existed and has been removed, False otherwise.
        """
        weekday_events = self.timetable[event.weekday - 1]
        if weekday_events.index(event) >= 0:
            weekday_events.remove(event)
            return True
        return False
