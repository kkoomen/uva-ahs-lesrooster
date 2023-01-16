from collections.abc import Generator

from code.entities.event import Event
from code.utils.helpers import remove_duplicates


class Timeslot:
    """
    Timeslots are used inside the Timetable class and contain scheduled events.

    Constraints:
    - Each timeslot can contain each room at most once.
    - Each timeslot can contain an event of a certain course at most once.
    - Only the largest room can be scheduled in the 17-19 timeframe.
    - Three (or more) empty timeslots in-between two other timeslots per student is not allowed.

    Malus points:
    - The 17:00 - 19:00 timeslot adds 5 malus points.
    - Each empty timeslot in-between two other timeslots per student adds 1 malus point.
    - Two empty timeslots in-between two other timeslots per student adds 3 malus points.
    - Every course conflict that each student has adds 1 malus point.
    - Every student that does not fit into the booked room adds 1 malus point.
    """

    OPTIONS = [9, 11, 13, 15, 17]
    TIMEFRAME = 2

    def __init__(self, value: int) -> None:
        self.value = value
        self.events = []

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

    def get_total_events(self) -> int:
        """
        Get the total amount of events.
        """
        return len(self.events)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(events:{len(self.events)})'

    def __iter__(self) -> Generator:
        """
        Allows to iterate over the timeslot events.
        """
        for event in self.events:
            yield event

    def get_duplicate_course_events(self) -> list[Event]:
        """
        Find duplicate events for a specific course in a certain timeslot.
        """
        duplicated_events = []
        visited_courses = []

        for event in self.events:
            if event.course in visited_courses:
                duplicated_events.append(event)
            else:
               visited_courses.append(event.course)

        return duplicated_events

    def get_double_booked_events(self) -> list[Event]:
        """
        Find the events that are booked in the same room.
        """
        double_booked_events = []
        visited_room_ids = []

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

    def calculate_malus_score(self) -> int:
        """
        Calculates the malus score for this particular timeslot.
        """
        points = 0

        # The 17:00 - 19:00 timeslot adds 5 malus points.
        if self.value == 17:
            points += 5

        # Add one malus punt for each overlapping course each student has.
        points += len(self.get_overlapping_student_courses_events())

        # Add one malus point for each student that does not fit into each room.
        points += self.calculate_room_overfitting_malus_score()

        return points

    def get_overlapping_student_courses_events(self) -> list[Event]:
        """
        Find the events that overlap in this timeslot for each student.
        """
        overlapping_events = []

        # Find all the courses that are overlapping for each student.
        # If the student id is already inside this list, then any other event
        # will be considered an overlapping event.
        student_ids = []
        for event in self.events:
            for student in event.students:
                if student.student_number not in student_ids:
                    student_ids.append(student.student_number)
                elif event not in overlapping_events:
                    overlapping_events.append(event)

        return overlapping_events

    def get_violations(self) -> list[Event]:
        """
        Get all events that are violating the constraints.
        """
        violations = []

        violations += self.get_timeslot_17_violations()
        violations += self.get_duplicate_course_events()
        violations += self.get_double_booked_events()

        return remove_duplicates(violations)
