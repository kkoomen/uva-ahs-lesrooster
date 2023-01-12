import csv
import os
from code.entities.event import Event
import matplotlib.pyplot as plt
from code.utils.constants import OUT_DIR, WEEKDAYS


class Timetable:
    """
    A single timetable can contain events that can be added or removed.

    An example timetable structure is described below:
    [
        [ // monday
            Event(type:hc, timeslot:9, room:C0.110, weekday:1, student_numbers:[1,2...]),
            Event(type:hc, timeslot:9, room:C1.04, weekday:1, student_numbers:[1,2...]),
            Event(type:hc, timeslot:11, room:C0.110, weekday:1, student_numbers:[1,2...]),
        ],
        [ // tuesday ],
        [ // wednesday
            Event(type:hc, timeslot:9, room:C1.08, weekday:3, student_numbers:[1,2...]),
        ],
        [ // thursday ],
        [ // friday ],
    ]
    """

    def __init__(self) -> None:
        self.timetable: list[list[Event]] = [[], [], [], [], []]

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
        if weekday_events.index(event) >= 0:
            weekday_events.remove(event)
            return True
        return False

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
