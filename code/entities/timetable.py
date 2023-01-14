from collections.abc import Generator
import csv
import logging
import os

from code.entities.event import Event
from code.entities.room import Room
from code.entities.timeslot import Timeslot
from code.utils.constants import OUT_DIR
from code.utils.data import load_courses, load_rooms, load_students
from code.utils.enums import Weekdays
import matplotlib.pyplot as plt


class Timetable:
    """
    A single timetable can contain events that can be added or removed.

    An example timetable structure is described below:
    [
        {
            9: Timeslot(events:[
                Event(type:hc, timeslot:9, room:C0.110, weekday:1, student:[Student, Student]),
                Event(type:hc, timeslot:9, room:C1.04, weekday:1, student:[Student, Student]),
            ])
            11: Timeslot(events:[
                Event(type:hc, timeslot:11, room:C0.110, weekday:1, student:[Student]),
            ])
        }
        { // tuesday },
        { // wednesday
            9: Timeslot(events:[
                Event(type:hc, timeslot:9, room:C1.08, weekday:3, student:[Student]),
            ])
        },
        { // thursday },
        { // friday },
    ]
    """

    MAX_TIMESLOTS_PER_WEEK = 145

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

        self.timetable: list[dict[int, Timeslot]] = [{}, {}, {}, {}, {}]
        self.rooms = load_rooms()
        self.courses = load_courses()
        self.students = load_students()

        self.largest_room = self.get_largest_room()

        self.register_students_to_courses()

    def __iter__(self) -> Generator:
        for day in self.timetable:
            yield day

    def register_students_to_courses(self):
        """
        Register all the students to the courses that they signed up for.
        """
        for course in self.courses:
            students = [s for s in self.students if course.name in s.enrolled_courses]
            course.register_students(students)

    def get_largest_room(self) -> Room:
        """
        Find the room that has the most capacity.
        """
        largest_room = self.rooms[0]

        for room in self.rooms:
            if room.capacity > largest_room.capacity:
                largest_room = room

        return largest_room

    def is_largest_room(self, room: Room) -> bool:
        """
        Check if the room is the largest room.
        """
        return room.location_id == self.largest_room.location_id

    def add_event(self, event: Event) -> None:
        """
        Add a single event to the timetable.
        """
        weekday = self.timetable[event.weekday - 1]

        if event.timeslot not in weekday:
            weekday[event.timeslot] = Timeslot(event.timeslot)

        weekday[event.timeslot].add_event(event)

    def remove_event(self, event: Event) -> None:
        """
        Remove a single event from the timetable.
        """
        self.timetable[event.weekday - 1][event.timeslot].remove_event(event)

    def remove_events(self, events: list[Event]) -> None:
        """
        Remove a list of events.
        """
        for event in events:
            self.remove_event(event)

    def get_total_timeslots(self) -> int:
        """
        Calculates the amount of timeslots for a week. Each timeslot is (for
        simplicity) a 2-hour timeslot. Available timeslots are 9-11, 11-13,
        13-15 and 15-17 for all rooms. The room with the most capacity contains
        an additional timeslot from 17-19, therefore the maximum amount of
        timeslots in a week is 145, meaning that the returned number will be
        less or equal than the maximum value.
        """
        total = 0

        for day in self.timetable:
            for timeslot in day.values():
                total += timeslot.get_total_events()

        return total

    def calculate_malus_score(self) -> int:
        """
        Calculates the malus score for the timetable. The perfect score is 0,
        and anything higher is bad.
        """
        score = 0

        for day in self.timetable:
            for timeslot in day.values():
                score += timeslot.calculate_malus_score()

        return score

    def is_valid(self) -> bool:
        """
        Check if the timetable structure is valid by checking constraints.
        """
        return len(self.get_violations()) == 0 and \
            self.get_total_timeslots() <= self.MAX_TIMESLOTS_PER_WEEK

    def get_violations(self) -> list[Event]:
        """
        Returns the events that violate the constraints.
        """
        violations = []

        for day in self.timetable:
            for (hour, timeslot) in day.items():
                # Timeslot 17 (17:00 - 19:00) can contain only one booking and
                # can only be booked in the largest room.
                if hour == 17:
                    # We can only have 1 booking at most, so discard everything
                    # besides the first booking.
                    valid_events = [event for event in timeslot if self.is_largest_room(event.room)]
                    violations += valid_events[1:]

                    # Those that are booked from 17:00 that are not in the
                    # largest room are violations.
                    invalid_events = [event for event in timeslot if not self.is_largest_room(event.room)]
                    violations += invalid_events
                else:
                    violations += timeslot.get_violations()

        return violations

    def clear(self) -> None:
        """
        Remove all data from the timetable.
        """
        self.timetable = [{}, {}, {}, {}, {}]

    def export_csv(self, filename: str) -> None:
        """
        Export the timetable data to a CSV.

        Below is an example of the exported data:
        student name,course,type,weekday,timeslot,room
        'John Doe','Algortimen en Heuristieken','hc','ma',9,'C0.110'
        'Mary Jane','Algortimen en Heuristieken','hc','ma',9,'C0.110'
        'Mike Smith','Algortimen en Heuristieken','hc','ma',9,'C0.110'
        'Lisa Gold','Programming 2','hc','ma',9,'C1.04'
        'Lisa Gold','Programming 2','hc','ma',9,'C1.04'
        """
        filepath = os.path.join(OUT_DIR, filename)
        rows = 0
        with open(filepath, 'w') as file:
            writer = csv.writer(file, quoting=csv.QUOTE_MINIMAL)

            # Write the header.
            writer.writerow(['student name', 'course', 'type', 'weekday',
                             'timeslot', 'room'])

            # Write all the other rows.
            for day in self.timetable:
                for timeslot in day.values():
                    for event in timeslot:
                        for student in event.course.enrolled_students:
                            row = [
                                student.get_full_name(),
                                event.title,
                                event.type,
                                Weekdays(event.weekday).name,
                                event.timeslot,
                                event.room.location_id
                            ]

                            rows += 1
                            writer.writerow(row)
            file.close()

        self.logger.info(f'Successfully saved timetable with {rows} records as {filepath}')

    def show_plot(self) -> None:
        """
        Plot all the events in the timetable.
        """
        # Create a list of timeslots to be used as the y-axis.
        timeslots = Timeslot.OPTIONS

        # Create a list of days to be used as the x-axis.
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']

        # Create a 2D array of zeros with the same shape as the timetable list.
        events = [[0 for _ in range(len(timeslots))] for _ in range(len(days))]

        # Add 1 for each event that is scheduled in that timeslot.
        for i, day in enumerate(self.timetable):
            for timeslot in day.values():
                for event in timeslot:
                    j = timeslots.index(event.timeslot)
                    events[j][i] += 1

        # Create a heatmap of the events.
        plt.imshow(events, cmap='gray_r', extent=[-0.5, len(days)-0.5,
                                                  len(timeslots)-0.5, -0.5])

        # Create the x-axis and y-axis ticks.
        plt.xticks(range(len(days)), days)
        plt.yticks(range(len(timeslots)), [f'{t}:00 - {t+2}:00' for t in timeslots])

        # Adding the amount of events scheduled for each timeslot.
        for i in range(len(days)):
            for j in range(len(timeslots)):
                if events[j][i] != '':
                    plt.text(i, j, events[j][i], ha='center', va='center',
                             color='r', fontweight='bold', fontsize='x-large')

        plt.gca().set_title('Timetable')
        plt.show()
