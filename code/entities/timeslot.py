from collections.abc import Generator
from typing import Union
from code.entities.course import Course

from code.entities.event import Event
from code.utils.helpers import remove_duplicates


class Timeslot:
    """
    Timeslots are used inside the Timetable class and contain scheduled events.
    """

    OPTIONS = [9, 11, 13, 15, 17]
    TIMEFRAME = 2

    def __init__(self, value: int, weekday: int, events: Union[list[Event], None]=None) -> None:
        self.value = value
        self.weekday = weekday
        self.events = events if events is not None else []

    def __eq__(self, other) -> bool:
        """
        Check if two timeslots are the same class type and value.
        """
        return self.__class__ == other.__class__ and \
            self.value == other.value and \
            self.weekday == other.weekday

    def add_event(self, event: Event) -> None:
        """
        Add an event to the events list.
        """
        self.events.append(event)

    def remove_event(self, event) -> None:
        """
        Remove an event from the events list.
        """
        self.events.remove(event)

    def __len__(self) -> int:
        """
        Implements len() usage.
        """
        return len(self.events)

    def get_total_events(self) -> int:
        """
        Get the total amount of events.
        """
        return len(self.events)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(value:{self.value}, events:{len(self.events)})'

    def __iter__(self) -> Generator:
        """
        Allows to iterate over the timeslot events.
        """
        for event in self.events:
            yield event

    def get_double_booked_violations(self) -> list[Event]:
        """
        Find the events that are booked in the same room.
        """
        double_booked_events = []
        visited_room_ids = []

        # Allow the first event we come across to be booked in a room and any
        # other event booked in the same room will be marked as a violation.
        for event in self.events:
            if event.room.location_id in visited_room_ids:
                double_booked_events.append(event)
            else:
                visited_room_ids.append(event.room.location_id)

        return double_booked_events

    def get_timeslot_17_violations(self) -> list[Event]:
        """
        Find the events that are booked at 17:00 but shouldn't.
        """
        violations = []

        # Timeslot 17 (17:00 - 19:00) can contain only one booking and can only
        # be booked in the largest room.
        if self.value == 17:
            # We can only have 1 booking at most, so discard everything
            # besides the first booking.
            valid_events = [event for event in self.events if event.room.is_largest]
            violations += valid_events[1:]

            # Those that are booked from 17:00 that are not in the
            # largest room are violations.
            invalid_events = [event for event in self.events if not event.room.is_largest]
            violations += invalid_events

        return violations

    def calculate_room_overfitting_malus_score(self) -> int:
        """
        Calculate a malus score that checks per room how much students do not
        into the room anymore. Each student too much adds one malus point.
        """
        score = 0

        for event in self.events:
            if len(event.students) > event.room.capacity:
                score += len(event.students) - event.room.capacity

        return score

    def calculate_timeslot_17_malus_score(self) -> int:
        """
        Calculcate the malus score whenever this timeslot is from 17:00 - 19:00.
        """
        points = 0

        largest_rooms = [event.room.is_largest for event in self.events]
        if self.value == 17 and any(largest_rooms):
            points += 5

        return points

    def calculate_duplicate_course_events_malus_score(self) -> int:
        """
        Calculate the malus score for each duplicate event of the same course.
        """
        score = 0

        visited_course_names = []
        for event in self.events:
            if event.course.name not in visited_course_names:
                visited_course_names.append(event.course.name)
            else:
                score += 1

        return score

    def calculate_malus_score(self) -> int:
        """
        Calculate the malus score for this particular timeslot.
        """
        points = 0

        # The 17:00 timeslot adds 5 points if the largest room is booked.
        points += self.calculate_timeslot_17_malus_score()

        # Add one malus punt for each overlapping course each student has.
        points += self.get_overlapping_student_courses_malus_score()

        # Add one malus point for each student that does not fit into each room.
        points += self.calculate_room_overfitting_malus_score()

        # Add one malus point for each duplicate event of the same course.
        points += self.calculate_duplicate_course_events_malus_score()

        return points

    def get_overlapping_student_courses_malus_score(self) -> int:
        """
        Find the events that overlap in this timeslot for each student.
        """
        score = 0

        # If the student id is already inside this list, then any other event
        # will be considered an overlapping event.
        student_ids = []

        # Group all events by student id.
        for event in self.events:
            for student in event.students:
                if student.student_id not in student_ids:
                    student_ids.append(student.student_id)
                else:
                    score += 1

        return score

    def get_violations(self) -> list[Event]:
        """
        Get all events that are violating the constraints.
        """
        violations = []

        violations += self.get_timeslot_17_violations()
        violations += self.get_double_booked_violations()

        return remove_duplicates(violations)

    def get_saturation_degree_for_course(self, course: Course) -> int:
        """
        Get the saturation degree which is the number of course conflicts.
        """
        saturation_degree = 0

        scheduled_course_names = remove_duplicates([event.course.name for event in self.events if event.course.name != course.name])
        for course_name in scheduled_course_names:
            if course_name in course.conflicting_courses:
                saturation_degree += 1

        return saturation_degree

    def serialize(self) -> list:
        """
        Serialize the data inside this class to a JSON-friendly structure.
        """
        return self.events
