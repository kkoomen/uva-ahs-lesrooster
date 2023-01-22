import abc
import copy
import random
from typing import Any, Union

from code.entities.event import Event
from code.entities.timeslot import Timeslot
from code.entities.timetable import Timetable
from code.utils.enums import EventType, Weekdays
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
        Run the algorithm for n-iterations until a valid solution is found.
        """
        pass

    def reassign_random_student_in_course(self, timetable: Union[Timetable, None]=None) -> None:
        """
        Seminars and practicals may contain 2 or more groups the students will
        be divided over. Take a random student from one of these groups and place it inside another group.
        """
        if timetable is None:
            timetable = self.timetable

        course = random.choice(timetable.courses)

        # The key will be a course name with the event type, i.e. 'Database wc'.
        # The value is a list of scheduled events for that course type.
        #
        # Example:
        # {
        #   'Databases wc': [Event(), Event(), Event()]
        #   'Databases pr': [Event(), Event()]
        # }
        course_events: dict[str, list[Event]] = {}

        for day in timetable:
            for timeslot in day.values():
                for event in timeslot:
                    if event.type not in course_events:
                        course_events[event.type] = []

                    if event.course == course and event.type != EventType.LECTURE:
                        course_events[event.type].append(event)

        # There might be seminars and practicals, so just choose one.
        selected_type = random.choice(list(course_events.keys()))
        events = course_events[selected_type]

        # Only put a student in another group if there are 2+ events.
        if len(events) >= 2:
            # Take a random event.
            event = events.pop(random.randrange(len(events)))
            if len(event.students) > 0 and len(event.students) < event.get_capacity():
                # Take a random student.
                student = event.students.pop(random.randrange(len(event.students)))

                # Assign student to any of the other events inside this course type.
                random.choice(events).add_student(student)

    def permute_students_for_random_course(self, timetable: Union[Timetable, None]=None) -> None:
        """
        Seminars and practicals may contain 2 or more groups the students will
        be divided over. Students will be permuted within either the seminar
        groups or the practicals for a single random course.
        """
        if timetable is None:
            timetable = self.timetable

        course = random.choice(timetable.courses)

        # The key will be a course name with the event type, i.e. 'Database wc'.
        # The value is a list of scheduled events for that course type.
        #
        # Example:
        # {
        #   'Databases wc': [Event(), Event(), Event()]
        #   'Databases pr': [Event(), Event()]
        # }
        course_events: dict[str, list[Event]] = {}

        for day in timetable:
            for timeslot in day.values():
                for event in timeslot:
                    if event.type not in course_events:
                        course_events[event.type] = []

                    if event.course == course and event.type != EventType.LECTURE:
                        course_events[event.type].append(event)

        # There might be seminars and practicals, so just choose one.
        selected_type = random.choice(list(course_events.keys()))
        events = course_events[selected_type]

        # Only permute among the events if there are 2 or more.
        if len(events) >= 2:
            # Gather all students.
            students = [student for event in events for student in event.students]

            # Divide the students in groups.
            student_groups = split_list_random(students, len(events))

            # Assign the students to the events.
            for i, event in enumerate(events):
                event.assign_students(student_groups[i])

    def swap_two_events(self, event: Event, other_event: Event, timetable: Union[Timetable, None]=None) -> None:
        """
        Swap two events with each other in the timetable.
        """
        if timetable is None:
            timetable = self.timetable

        assert event.room is not None, 'event must have a room'
        assert event.weekday is not None, 'event must have a weekday'
        assert event.timeslot is not None, 'event must have a timeslot'

        assert other_event.room is not None, 'other event must have a room'
        assert other_event.weekday is not None, 'other event must have a weekday'
        assert other_event.timeslot is not None, 'other event must have a timeslot'

        timetable.remove_event(event)
        timetable.remove_event(other_event)

        new_event = copy.deepcopy(event)
        new_event.set_room(other_event.room)
        new_event.set_weekday(other_event.weekday)
        new_event.set_timeslot(other_event.timeslot)

        other_new_event = copy.deepcopy(other_event)
        other_new_event.set_room(event.room)
        other_new_event.set_weekday(event.weekday)
        other_new_event.set_timeslot(event.timeslot)

        timetable.add_event(new_event)
        timetable.add_event(other_new_event)

    def create_similar_event(self, event: Event, timetable: Union[Timetable, None]=None) -> Event:
        """
        Clone the current event, but with other data than the it currently has.
        """
        if timetable is None:
            timetable = self.timetable

        timeslot = random.choice([n for n in Timeslot.OPTIONS if n != event.timeslot])
        weekday = random.choice([weekday.value for weekday in Weekdays])
        room = random.choice(timetable.rooms)
        return Event(event.title, event.type, event.course, weekday, timeslot, room, event.students)

    def move_random_event(self, timetable: Union[Timetable, None]=None) -> None:
        """
        Move a single event to another random timeslot.
        """
        if timetable is None:
            timetable = self.timetable

        events = timetable.get_events()
        event = random.choice(events)
        similar_event = self.create_similar_event(event, timetable)
        timetable.remove_event(event)
        timetable.add_event(similar_event)

    def swap_two_random_events(self, timetable: Union[Timetable, None]=None) -> None:
        """
        Swap two random events with each other.
        """
        if timetable is None:
            timetable = self.timetable

        events = timetable.get_events()
        event = events.pop(random.randrange(len(events)))
        other_event = events.pop(random.randrange(len(events)))

        self.swap_two_events(event, other_event, timetable)
