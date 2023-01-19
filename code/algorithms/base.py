import abc
import copy
from typing import Any

from code.entities.event import Event
from code.entities.timetable import Timetable
from code.utils.helpers import split_list_random


class Algorithm(abc.ABC):
    timetable: Timetable
    statistics: list[Any]

    @abc.abstractmethod
    def plot_statistics(self) -> None:
        """
        Plot statistics that were gathered when the algorithm ran.
        """
        pass

    @abc.abstractmethod
    def run(self, iterations: int) -> None:
        """
        Run the algorithm for n-iteraations until a valid solution is found.
        """
        pass

    def permute_students(self):
        """
        Permute students within the scheduled events inside a course. Seminars
        and practicals may contain 2 or more groups the students will be divided
        over. Students will be permuted within these groups.

        NOTE: Permuting for lectures doesn't make a difference, since it is
        mandatory that all students attend this.
        """
        # The key will be a course name with the event type, i.e. 'Database wc'.
        # The value is a list of scheduled events for that course type.
        #
        # Example:
        # {
        #   'Databases hc': [Event()]
        #   'Databases wc': [Event(), Event(), Event()]
        #   'Databases pr': [Event(), Event()]
        #   'Calculus 2 hc': [Event(), Event()]
        #   'Calculus 2 wc': [Event(), Event()]
        #   'Calculus 2 pr': [Event()]
        # }
        course_events: dict[str, list[Event]] = {}

        for day in self.timetable:
            for timeslot in day.values():
                for event in timeslot:
                    key = f'{event.course.name} {event.type}'

                    if key not in course_events:
                        course_events[key] = []

                    course_events[key].append(event)

        for events in course_events.values():
            # Only permute among the events if there are 2 or more.
            if len(events) >= 2:
                # Gather all students
                students = [student for event in events for student in event.students]

                # Divide the students in groups
                student_groups = split_list_random(students, len(events))

                # Assign the students to the events
                for i, event in enumerate(events):
                    event.assign_students(student_groups[i])

    def swap_two_events(self, event: Event, other_event: Event) -> None:
        """
        Swap two events with each other in the timetable.
        """
        assert event.room is not None, 'event must have a room'
        assert event.weekday is not None, 'event must have a weekday'
        assert event.timeslot is not None, 'event must have a timeslot'

        assert other_event.room is not None, 'other event must have a room'
        assert other_event.weekday is not None, 'other event must have a weekday'
        assert other_event.timeslot is not None, 'other event must have a timeslot'

        self.timetable.remove_event(event)
        self.timetable.remove_event(other_event)

        new_event = copy.deepcopy(event)
        new_event.set_room(other_event.room)
        new_event.set_weekday(other_event.weekday)
        new_event.set_timeslot(other_event.timeslot)

        other_event.set_room(event.room)
        other_event.set_weekday(event.weekday)
        other_event.set_timeslot(event.timeslot)

        self.timetable.add_event(new_event)
        self.timetable.add_event(other_event)
