#!/usr/bin/env python3


import copy
import logging
import random
from code.algorithms.greedy import Greedy

from code.entities.course import Course
from code.entities.event import Event
from code.entities.timeslot import Timeslot
from code.entities.timetable import Timetable
from code.utils.enums import EventType, Weekdays
from code.utils.helpers import split_list_random


class HillClimber(Greedy):
    """
    Hill climber algorithm implementation which grabs a random state and accepts
    it if it better than the previous state.
    """

    def __init__(self) -> None:
        self.timetable = Timetable()
        self.logger = logging.getLogger(__name__)

    def print_average_statistics(self, iterations: int) -> None:
        self.logger.info('TODO: implement print_average_statistics()')

    def swap_two_random_events(self) -> None:
        """
        Take two random events and swap them.
        """
        events = self.timetable.get_events()

        event = events.pop(random.randrange(len(events)))
        other_event = events.pop(random.randrange(len(events)))

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

    def create_random_event(self, title: str, event_type: EventType, course: Course) -> Event:
        """
        Create an event with a random timeslot, room and weekday.
        """
        timeslot = random.choice(Timeslot.OPTIONS)
        room = random.choice(self.timetable.rooms)
        weekday = random.choice([weekday.value for weekday in Weekdays])
        return Event(title, event_type, course, weekday, timeslot, room)

    def create_similar_event(self, event: Event) -> Event:
        """
        Clone the current event, but with other data than the it currently has.
        """
        timeslot = random.choice([n for n in Timeslot.OPTIONS if n != event.timeslot])
        weekday = random.choice([weekday.value for weekday in Weekdays])
        room = random.choice(self.timetable.rooms)
        return Event(event.title, event.type, event.course, weekday, timeslot, room, event.students)

    def move_random_event(self) -> None:
        """
        Move a single event to another random timeslot.
        """
        events = self.timetable.get_events()
        event = random.choice(events)
        self.timetable.remove_event(event)
        similar_event = self.create_similar_event(event)
        self.timetable.add_event(similar_event)

    def generate_state(self) -> None:
        """
        Run the parent algorithm in order to generate a solution.
        """
        super().run()

    def plot_statistics(self) -> None:
        """
        Plot the malus scores during the hill climber process.
        """
        pass

    def run(self) -> None:
        self.timetable.clear()
        self.generate_state()

        # Total iterations to do.
        iterations = 5000

        # Stop if there is no improvement anymore after this amount of times.
        no_improvement_limit = 500

        violations = len(self.timetable.get_violations())
        malus_score = self.timetable.calculate_malus_score()
        self.logger.info(f'Initial solution state has {violations} violations and {malus_score} malus score')

        prev_state = copy.deepcopy(self.timetable)
        no_improvement_counter = 0
        for i in range(iterations):
            if no_improvement_counter == no_improvement_limit:
                self.logger.info(f'Reached local optimum')
                return

            # Log the current iteration every 100 iterations.
            if i % 100 == 0:
                self.logger.debug(f'Starting iteration {i}/{iterations}')

            # 40% chance to change a single event
            # 50% chance to swap two random events
            # 10% to permute students
            n = random.random()
            if n < 0.4:
                self.move_random_event()
            elif 0.4 <= n < 0.9:
                self.swap_two_random_events()
            else:
                self.permute_students()

            # Violations should be checked as they are more important.
            violations = len(self.timetable.get_violations())
            malus_score = self.timetable.calculate_malus_score()
            prev_violations = len(prev_state.get_violations())
            prev_malus_score = prev_state.calculate_malus_score()

            is_better_solution = (
                violations <= prev_violations and \
                malus_score <= prev_malus_score
            )

            if is_better_solution:
                no_improvement_counter = 0
            else:
                no_improvement_counter += 1
                self.timetable = prev_state

            is_different_state = (
                violations != prev_violations or \
                violations == prev_violations and malus_score != prev_malus_score
            )

            if is_better_solution and is_different_state:
                self.logger.info(f'Found better state with {violations} violations and {malus_score} malus score')
            elif is_better_solution:
                self.logger.debug(f'Found similar state with {violations} violations and {malus_score} malus score')

            prev_state = copy.deepcopy(self.timetable)

        self.logger.info(f'Exceed total iterations')
