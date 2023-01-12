import csv
import os

from code.entities.event import Event
from code.entities.room import Room
from code.utils.constants import OUT_DIR, WEEKDAYS
from code.utils.data import load_courses, load_rooms, load_students
import matplotlib.pyplot as plt


class Timetable:
    """
    A single timetable can contain events that can be added or removed.

    Constraints:
    - Each timeslot can contain each room at most once.
    - Each timeslot can contain an event of a certain course at most once.
    - Only the biggest room can be scheduled inside the

    An example timetable structure is described below:
    [
        [ // monday
            Event(type:hc, timeslot:9, room:C0.110, weekday:1, student_numbers:[Student, Student]),
            Event(type:hc, timeslot:9, room:C1.04, weekday:1, student_numbers:[Student, Student]),
            Event(type:hc, timeslot:11, room:C0.110, weekday:1, student_numbers:[Student]),
        ],
        [ // tuesday ],
        [ // wednesday
            Event(type:hc, timeslot:9, room:C1.08, weekday:3, student_numbers:[Student]),
        ],
        [ // thursday ],
        [ // friday ],
    ]
    """

    def __init__(self) -> None:
        self.timetable: list[list[Event]] = [[], [], [], [], []]
        self.rooms = load_rooms()
        self.courses = load_courses()
        self.students = load_students()
        self.largest_room = self.get_largest_room()

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

    def add_event(self, event: Event) -> bool:
        """
        Add a single event to the timetable.

        :returns: True if the event has been added, False otherwise.
        """
        self.timetable[event.weekday - 1].append(event)
        return True

    def remove_event(self, event: Event) -> bool:
        """
        Remove a single event from the timetable.

        :returns: True if `event` existed and has been removed, False otherwise.
        """
        weekday_events = self.timetable[event.weekday - 1]

        try:
            for index, ev in enumerate(weekday_events):
                if ev.id == event.id:
                    weekday_events.pop(index)
                    return True
        except ValueError:
            pass
        finally:
            return False

    def remove_events(self, events: list[Event]) -> None:
        """
        Remove a list of events.
        """
        for event in events:
            self.remove_event(event)

    def get_events_by_weekday(self, weekday: int) -> list[Event]:
        """
        Get the events for a day by weekday (1-5 equals mon-fri)
        """
        return self.timetable[weekday - 1]

    def calculate_value(self) -> int:
        """
        Calculates the amount of timeslots for a week. Each timeslot is (for
        simplicity) a 2-hour timeslot. Available timeslots are 9-11, 11-13,
        13-15 and 15-17 for all rooms. The room with the most capacity contains
        an additional timeslot from 17-19, therefore the maximum amount of
        timeslots in a week is 145, meaning that the returned number will be
        less or equal than the maximum value.
        """
        return sum([len(day) for day in self.timetable])


    def get_day_timeslots(self, day: list[Event]) -> dict[int, list[Event]]:
        """
        Group the events inside a day based on their timeslot time.
        """
        timeslots = {}

        for event in day:
            if event.timeslot not in timeslots:
                timeslots[event.timeslot] = []

            timeslots[event.timeslot].append(event)

        return timeslots

    def is_valid(self) -> bool:
        """
        Check if the timetable structure is valid by checking constraints.
        """
        return len(self.get_violations()) == 0

    def get_timeslot_duplicate_course_events(self, timeslot: list[Event]) -> list[Event]:
        """
        Find duplicate events for a specific course in a certain timeslot.
        """
        duplicated_events = []
        visited_course_names = []

        for event in timeslot:
            if event.course.name in visited_course_names:
                duplicated_events.append(event)
            else:
                visited_course_names.append(event.course.name)

        return duplicated_events

    def get_timeslot_double_booked_events(self, timeslot: list[Event]) -> list[Event]:
        """
        Find the events that are booked in the same room.
        """
        double_booked_events = []
        visited_room_ids = []

        for event in timeslot:
            if event.room.location_id in visited_room_ids:
                double_booked_events.append(event)
            else:
                visited_room_ids.append(event.room.location_id)

        return double_booked_events

    def get_violations(self) -> list[Event]:
        """
        Returns the events that violate the constraints.
        Constraints are specified above in the class docblock.
        """
        violations = []

        for day in self.timetable:
            timeslots = self.get_day_timeslots(day)
            for (timeframe, timeslot) in timeslots.items():
                # Timeframe 17 (17:00 - 19:00) can contain only one booking and
                # can only be booked in the largest room.
                if timeframe == 17:
                    # We can only have 1 booking at most, so discard everything
                    # besides the first booking.
                    valid_events = [event for event in timeslot if self.is_largest_room(event.room)]
                    violations += valid_events[1:]

                    # Those that are booked from 17:00 that are not in the
                    # largest room are violations.
                    invalid_events = [event for event in timeslot if not self.is_largest_room(event.room)]
                    violations += invalid_events
                else:
                    violations += self.get_timeslot_duplicate_course_events(timeslot)
                    violations += self.get_timeslot_double_booked_events(timeslot)

        return violations


    def export_csv(self, filename: str, verbose=False) -> None:
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

            # Write the header
            writer.writerow(['student name', 'course', 'type', 'weekday',
                             'timeslot', 'room'])

            for day in self.timetable:
                for event in day:
                    for student in event.enrolled_students:
                        row = [
                            student.get_full_name(),
                            event.title,
                            event.type,
                            WEEKDAYS[event.weekday - 1],
                            event.timeslot,
                            event.room.location_id
                        ]

                        rows += 1
                        writer.writerow(row)
            file.close()

        if verbose:
            print(f'Succesfully saved timetable with {rows} records as {filepath}')

    def print_info(self) -> None:
        """
        Print timetable information.
        """
        for i, day in enumerate(self.timetable):
            print(f'{WEEKDAYS[i]}: {len(day)}')

    def show_plot(self) -> None:
        """
        Plot all the events in the timetable.
        """
        # Create a list of timeslots to be used as the y-axis.
        timeslots = [9, 11, 13, 15, 17]

        # Create a list of days to be used as the x-axis.
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']

        # Create a 2D array of zeros with the same shape as the timetable list.
        events = [[0 for _ in range(len(timeslots))] for _ in range(len(days))]

        # Iterate through the timetable and add 1 for each event that is
        # schedules in that timeslot.
        for i, day in enumerate(self.timetable):
            for event in day:
                j = timeslots.index(event.timeslot)
                events[j][i] += 1

        # Create a heatmap of the events.
        plt.imshow(events, cmap='gray_r', extent=[-0.5, len(days)-0.5,
                                                  len(timeslots)-0.5, -0.5])

        # Create the x-axis and y-axis ticks.
        plt.xticks(range(len(days)), days)
        plt.yticks(range(len(timeslots)), [f'{t}:00 - {t+2}:00' for t in timeslots])

        # iterate over data and adding the roomname to the corresponding cell
        for i in range(len(days)):
            for j in range(len(timeslots)):
                if events[j][i] != '':
                    plt.text(i, j, events[j][i], ha='center', va='center', color='r')

        plt.show()
