import copy
import logging
import random

from code.entities.event import Event
from code.entities.student import Student
from code.entities.timeslot import Timeslot
from code.entities.timetable import Timetable


class Randomizer:

    def __init__(self, timetable: Timetable) -> None:
        self.timetable = copy.deepcopy(timetable)
        self.logger = logging.getLogger(__name__)

    def create_random_event(self, title, course, event_type: str) -> Event:
        """
        Create an event with random timeslot, room and weekday.
        """
        timeslot = random.choice(Timeslot.OPTIONS)
        room = random.choice(self.timetable.rooms)
        weekday = random.choice([1, 2, 3, 4, 5])
        return Event(title, event_type, timeslot, course, room, weekday)

    def create_similar_event(self, event) -> Event:
        """
        Clone the current event, but with other data than itself.
        """
        timeslot = random.choice([n for n in Timeslot.OPTIONS if n != event.timeslot])
        room = random.choice([r for r in self.timetable.rooms if r != event.room])
        weekday = random.choice([n for n in [1, 2, 3, 4, 5] if n != event.weekday])
        return Event(event.title, event.type, timeslot, event.course, room, weekday)

    def assign_random_events(self) -> None:
        """
        Creates random events based on the courses data.
        """
        for course in self.timetable.courses:
            for _ in range(course.lectures_amount):
                event = self.create_random_event(f'{course.name} hoorcollege', course, 'hc')
                self.timetable.add_event(event)

            for _ in range(course.seminars_amount):
                event = self.create_random_event(f'{course.name} werkcollege', course, 'wc')
                self.timetable.add_event(event)

            for _ in range(course.practicals_amount):
                event = self.create_random_event(f'{course.name} practicum', course, 'pr')
                self.timetable.add_event(event)

    def reassign_events(self, events: list[Event]) -> None:
        """
        Reassign a list of events but with some changes to the values.
        """
        self.timetable.remove_events(events)
        for event in events:
            new_event = self.create_similar_event(event)
            self.timetable.add_event(new_event)

    def run(self) -> None:
        """
        Assign random events until the timetable is valid.
        """
        self.assign_random_events()
        violations = self.timetable.get_violations()

        retries = 0
        while len(violations) > 0:
            retries += 1

            self.logger.debug(f'[RETRY #{retries}] Found {len(violations)} violations, going to reassign them...')

            self.reassign_events(violations)
            violations = self.timetable.get_violations()

        self.logger.info(f'[DONE] Successfully created random timetable (retries:{retries})')
