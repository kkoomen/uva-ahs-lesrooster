import logging
import math
import random

from code.algorithms.base import Algorithm
from code.entities.course import Course
from code.entities.event import Event
from code.entities.room import Room
from code.entities.timeslot import Timeslot
from code.entities.timetable import Timetable
from code.utils.enums import Weekdays
from code.utils.helpers import split_list_random


class Randomizer(Algorithm):
    """
    This algorithm will create random events in the timetable and reassign any
    of the events that violate the constraints.
    """

    def __init__(self) -> None:
        self.timetable = Timetable()
        self.logger = logging.getLogger(__name__)

    def create_random_event(self, title: str, event_type: str, course: Course) -> Event:
        """
        Create an event with random timeslot, room and weekday.
        """
        timeslot = random.choice(Timeslot.OPTIONS)
        room = random.choice(self.timetable.rooms)
        weekday = random.choice([weekday.value for weekday in Weekdays])
        return Event(title, event_type, timeslot, course, room, weekday)

    def create_similar_event(self, event: Event) -> Event:
        """
        Clone the current event, but with other data than itself.
        """
        timeslot = random.choice([n for n in Timeslot.OPTIONS if n != event.timeslot])
        weekday = random.choice([weekday.value for weekday in Weekdays])
        room = random.choice(self.timetable.rooms)
        return Event(event.title, event.type, timeslot, event.course, room, weekday, event.students)

    def assign_random_events(self) -> None:
        """
        Creates random events based on the courses data.
        """
        for course in self.timetable.courses:
            for i in range(course.lectures_amount):
                event = self.create_random_event(f'{course.name} hoorcollege {i + 1}', 'hc', course)
                event.assign_students(course.enrolled_students)
                self.timetable.add_event(event)

            for _ in range(course.seminars_amount):
                # Create groups based on the seminar capacity and enrolment.
                total_groups = math.ceil(course.enrolment / course.seminar_capacity)
                group_capacity = math.ceil(course.enrolment / total_groups)
                student_groups = split_list_random(course.enrolled_students, group_capacity)
                for i in range(total_groups):
                    event = self.create_random_event(f'{course.name} werkcollege {i + 1}', 'wc', course)
                    event.assign_students(student_groups[i])
                    self.timetable.add_event(event)

            for _ in range(course.practicals_amount):
                # Create groups based on the practicals capacity and enrolment.
                total_groups = math.ceil(course.enrolment / course.practical_capacity)
                group_capacity = math.ceil(course.enrolment / total_groups)
                student_groups = split_list_random(course.enrolled_students, group_capacity)
                for i in range(total_groups):
                    event = self.create_random_event(f'{course.name} practicum {i + 1}', 'pr', course)
                    event.assign_students(student_groups[i])
                    self.timetable.add_event(event)

    def reassign_events(self, events: list[Event]):
        """
        Reassign a list of events but with some changes to the values.
        """
        reassigned_events = []

        self.timetable.remove_events(events)
        for event in events:
            new_event = self.create_similar_event(event)
            reassigned_events.append(new_event)
            self.timetable.add_event(new_event)

        return reassigned_events

    def swap_events(self, events: list[Event]) -> None:
        """
        Swap each event with any random other event in the timetable.
        """
        # Gather all other timetable events.
        other_events = []
        for day in self.timetable:
            for timeslot in day.values():
                for event in timeslot:
                    if event not in events:
                        other_events.append(event)

        # Swap the events with any other random event.
        for event in events:
            other_event = random.choice(other_events)

            self.timetable.remove_event(event)
            self.timetable.remove_event(other_event)

            event.set_weekday(other_event.weekday)
            event.set_timeslot(other_event.timeslot)
            other_event.set_weekday(event.weekday)
            other_event.set_timeslot(event.timeslot)

            self.timetable.add_event(event)
            self.timetable.add_event(other_event)

    def swap_students(self):
        """
        Swap students in the whole timetable. The swapping will only be done
        within the scheduled events inside a course. Seminars and practicals may
        contain 2 or more groups the students will be divided over. Students
        will be swapped within these groups.
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
            # Only swap among the events if there are 2 or more.
            if len(events) >= 2:
                # Gather all students
                students = [student for event in events for student in event.students]

                # Divide the students in groups
                student_groups = split_list_random(students, len(events))

                # Assign the students to the events
                for i, event in enumerate(events):
                    event.assign_students(student_groups[i])

    def run(self) -> tuple[bool, int]:
        """
        Assign random events until the timetable is valid.
        """
        self.timetable.clear()
        self.assign_random_events()
        violations = self.timetable.get_violations()

        max_retries = 5000
        found_solution = True
        retries = 0
        while len(violations) > 0:
            retries += 1

            self.logger.debug(f'[RETRY #{retries}] Found {len(violations)} violations, going to reassign them...')

            # Sometimes it might run into an infinite loop, so if the retries is
            # above a certain threshold, we stop trying.
            if retries >= max_retries:
                found_solution = False
                break

            violations = self.reassign_events(violations)
            if random.random() < 0.1:
                self.swap_events(violations)
            if random.random() < 0.01:
                self.swap_students()
            violations = self.timetable.get_violations()

        if found_solution:
            self.logger.info(f'[DONE] Successfully created random timetable (retries:{retries})')
        else:
            self.logger.info(f'[DONE] Failed to create random timetable, exceeded max retries (retries:{retries})')

        return found_solution, retries
