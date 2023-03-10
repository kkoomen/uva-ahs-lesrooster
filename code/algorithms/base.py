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

        new_other_event = copy.deepcopy(other_event)
        new_other_event.set_room(event.room)
        new_other_event.set_weekday(event.weekday)
        new_other_event.set_timeslot(event.timeslot)

        timetable.add_event(new_event)
        timetable.add_event(new_other_event)

    def create_similar_event(self, event: Event, timetable: Union[Timetable, None]=None) -> Event:
        """
        Clone the current event, but with other data than the it currently has.
        """
        if timetable is None:
            timetable = self.timetable

        new_event = copy.deepcopy(event)

        # Put the timeslot in any other timeslot than the current one.
        timeslot = random.choice(Timeslot.OPTIONS)
        if timeslot == event.timeslot:
            weekday = random.choice([weekday.value for weekday in Weekdays if weekday.value != event.weekday])
        else:
            weekday = random.choice([weekday.value for weekday in Weekdays])

        room = random.choice(timetable.rooms)

        new_event.set_timeslot(timeslot)
        new_event.set_weekday(weekday)
        new_event.set_room(room)

        return new_event

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

    def move_high_malus_score_events(self, timetable: Union[Timetable, None]=None) -> None:
        """
        Find the timeslot with the highest malus score and move one of the
        events to another timeslot giving the least conflict for that event.
        """
        if timetable is None:
            timetable = self.timetable

        # Find all timeslots with a non-zero malus score.
        timeslots = []
        for day in timetable:
            for timeslot in day.values():
                if timeslot.calculate_malus_score() > 0:
                    timeslots.append(timeslot)

        # Take a random timeslot from those that still have malus points > 0.
        current_timeslot = random.choice(timeslots)

        # Take one of the events inside the timeslot.
        event = random.choice(current_timeslot.events)

        # Find the best timeslot for this event with the least course conflicts.
        other_timeslot = None
        lowest_degree = None
        for day in timetable:
            for timeslot in day.values():
                if timeslot == current_timeslot:
                    continue

                saturation_degree = timeslot.get_saturation_degree_for_course(event.course)
                if lowest_degree is None or saturation_degree < lowest_degree:
                    lowest_degree = saturation_degree
                    other_timeslot = timeslot

        if isinstance(other_timeslot, Timeslot) and len(other_timeslot.events) > 0:
            # Get another event from this timeslot.
            other_event = random.choice(other_timeslot.events)

            # Swap the two events.
            self.swap_two_events(event, other_event, timetable)

    def mutate_state(self, timetable: Union[Timetable, None]=None) -> None:
        """
        Mutate the timetable with some random actions.

        The actions are as follows:
        - 30% chance to move one an event with malus score > 0
        - 30% chance to move a single event
        - 30% chance to swap two random events
        - 10% chance to permute students within a course
        """
        if timetable is None:
            timetable = self.timetable

        n = random.random()
        if n < 0.3:
            self.move_high_malus_score_events(timetable)
        elif 0.3 <= n < 0.6:
            self.move_random_event(timetable)
        elif 0.6 <= n < 0.9:
            self.swap_two_random_events(timetable)
        else:
            self.permute_students_for_random_course(timetable)
