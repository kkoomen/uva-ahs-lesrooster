import copy
import random

from code.entities.event import Event
from code.entities.student import Student
from code.entities.timetable import Timetable


class Randomizer:

    def __init__(self, timetable: Timetable) -> None:
        self.timetable = copy.deepcopy(timetable)

    def get_random_students(self) -> list[Student]:
        """
        Get random students.

        TODO: do randint() upper- and lowerbound based on `event`.
        """
        return random.choices(self.timetable.students, k=random.randint(8, 40))

    def create_random_event(self, title, course, event_type: str) -> Event:
        """
        Create an event with random timeslot, room and weekday.
        """
        timeslot = random.choice([9, 11, 13, 15, 17])
        room = random.choice(self.timetable.rooms)
        weekday = random.choice([1, 2, 3, 4, 5])
        students = self.get_random_students()
        return Event(title, event_type, timeslot, course, room, weekday, students)

    def create_similar_event(self, event) -> Event:
        """
        Clone the current event, but with other data.
        """
        timeslot = random.choice([n for n in [9, 11, 13, 15, 17] if n != event.timeslot])
        room = random.choice([r for r in self.timetable.rooms if r.location_id != event.room.location_id])
        weekday = random.choice([n for n in [1, 2, 3, 4, 5] if n != event.weekday])
        students = self.get_random_students()
        return Event(event.title, event.type, timeslot, event.course, room, weekday, students)

    def assign_random_events(self) -> None:
        """
        Creates random events based on the courses data.
        """
        for course in self.timetable.courses:
            for _ in range(course.lectures_amount):
                event = self.create_random_event(f'{course.name} (HC)', course, 'hc')
                self.timetable.add_event(event)

            for _ in range(course.seminars_amount):
                event = self.create_random_event(f'{course.name} (WC)', course, 'wc')
                self.timetable.add_event(event)

            for _ in range(course.practicals_amount):
                event = self.create_random_event(f'{course.name} (PR)', course, 'pr')
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
        print(f'initial value: {self.timetable.calculate_value()}')

        while len(violations) > 0:
            # self.timetable.print_info()
            self.reassign_events(violations)
            violations = self.timetable.get_violations()

            # The maximum value (amount of timeslots) can be 145. To prevent an
            # infinite loop, we make sure to stop if it has more than 145 timeslots.
            if self.timetable.calculate_value() > 145:
                break
