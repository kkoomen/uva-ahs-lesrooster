import copy
import logging
import math
import random
from code.entities.course import Course

from code.entities.event import Event
from code.entities.room import Room
from code.entities.timeslot import Timeslot
from code.entities.timetable import Timetable
from code.utils.enums import Weekdays
from code.utils.helpers import split_list_random


class Randomizer:

    def __init__(self, timetable: Timetable) -> None:
        self.timetable = copy.deepcopy(timetable)
        self.logger = logging.getLogger(__name__)

    def create_random_event(self, title: str, event_type: str, course: Course,
                            room: Room) -> Event:
        """
        Create an event with random timeslot, room and weekday.
        """
        timeslot = random.choice(Timeslot.OPTIONS)
        weekday = random.choice([weekday.value for weekday in Weekdays])
        return Event(title, event_type, timeslot, course, room, weekday)

    def create_similar_event(self, event: Event) -> Event:
        """
        Clone the current event, but with other data than itself.
        """
        timeslot = random.choice([n for n in Timeslot.OPTIONS if n != event.timeslot])
        weekday = random.choice([weekday.value for weekday in Weekdays])

        if event.type == 'hc':
            room = random.choice([r for r in self.timetable.rooms if r.capacity >= event.course.enrolment])
        elif event.type == 'wc':
            total_groups = math.ceil(event.course.enrolment / event.course.seminar_capacity)
            group_capacity = math.ceil(event.course.enrolment / total_groups)
            room = random.choice([r for r in self.timetable.rooms if r.capacity >= group_capacity])
        else: # practicals
            total_groups = math.ceil(event.course.enrolment / event.course.practical_capacity)
            group_capacity = math.ceil(event.course.enrolment / total_groups)
            room = random.choice([r for r in self.timetable.rooms if r.capacity >= group_capacity])

        return Event(event.title, event.type, timeslot, event.course, room, weekday)

    def assign_random_events(self) -> None:
        """
        Creates random events based on the courses data.
        """
        for course in self.timetable.courses:
            for _ in range(course.lectures_amount):
                room = random.choice([r for r in self.timetable.rooms if r.capacity >= course.enrolment])
                event = self.create_random_event(f'{course.name} hoorcollege', 'hc', course, room)
                self.timetable.add_event(event)

            for _ in range(course.seminars_amount):
                # Create groups based on the seminar capacity and enrolment.
                total_groups = math.ceil(course.enrolment / course.seminar_capacity)
                group_capacity = math.ceil(course.enrolment / total_groups)
                student_groups = split_list_random(course.enrolled_students, group_capacity)
                for i in range(total_groups):
                    room = random.choice([r for r in self.timetable.rooms if r.capacity >= group_capacity])
                    event = self.create_random_event(f'{course.name} werkcollege {i + 1}', 'wc', course, room)
                    event.assign_students(student_groups[i])
                    self.timetable.add_event(event)

            for _ in range(course.practicals_amount):
                # Create groups based on the practicals capacity and enrolment.
                total_groups = math.ceil(course.enrolment / course.practical_capacity)
                group_capacity = math.ceil(course.enrolment / total_groups)
                student_groups = split_list_random(course.enrolled_students, group_capacity)
                for i in range(total_groups):
                    room = random.choice([r for r in self.timetable.rooms if r.capacity >= group_capacity])
                    event = self.create_random_event(f'{course.name} practicum {i + 1}', 'pr', course, room)
                    event.assign_students(student_groups[i])
                    self.timetable.add_event(event)

    def reassign_events(self, events: list[Event]) -> None:
        """
        Reassign a list of events but with some changes to the values.
        """
        self.timetable.remove_events(events)
        for event in events:
            new_event = self.create_similar_event(event)
            self.timetable.add_event(new_event)

    def run(self) -> int:
        """
        Assign random events until the timetable is valid.

        :returns: The total amount of retries.
        """
        self.assign_random_events()
        violations = self.timetable.get_violations()

        retries = 0
        while len(violations) > 0:
            retries += 1

            self.logger.debug(f'[RETRY #{retries}] Found {len(violations)} violations, going to reassign them...')

            # Because the students are not swapped in the violations, it might
            # run into an infinite loop, so if the retries is above a certaint
            # threshold, we stop trying.
            if retries >= 200:
                self.logger.debug(violations)
                break

            self.reassign_events(violations)
            violations = self.timetable.get_violations()

        self.logger.info(f'[DONE] Successfully created random timetable (retries:{retries})')

        return retries
