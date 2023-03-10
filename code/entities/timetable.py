from collections.abc import Generator
import copy
import csv
from datetime import datetime, timedelta
import itertools
import json
import logging
import os
import re
import ics
import matplotlib.pyplot as plt
import networkx as nx

from code.entities.event import Event
from code.entities.room import Room
from code.entities.timeslot import Timeslot
from code.utils.constants import OUT_DIR
from code.utils.data import load_courses, load_rooms, load_students
from code.utils.enums import Weekdays
from code.utils.helpers import get_utc_offset, remove_duplicates, serialize


TimetableDay = dict[int, Timeslot]
TimetableList = list[TimetableDay]


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
    DAYS_PER_WEEK = 5

    def __init__(self,
                 load_rooms=load_rooms,
                 load_courses=load_courses,
                 load_students=load_students) -> None:
        self.logger = logging.getLogger(__name__)

        self.timetable: TimetableList = self.new_timetable()
        self.rooms = load_rooms()
        self.courses = load_courses()
        self.students = load_students()

        self.set_course_conflicts()
        self.register_students_to_courses()

    def set_course_conflicts(self) -> None:
        """
        Create a graph where each vertice represents a course and the edge in
        between two vertices indicates that there is at least one student
        enrolled in both courses, meaning that all neighbors for a node in the
        graph represent the conflicting courses for a course respectively.
        """
        # Create the graph.
        network = nx.Graph()
        network.add_nodes_from([course.name for course in self.courses])

        # Get all courses that are overlapping for each student.
        list_of_overlaps = [student.enrolled_courses for student in self.students]

        # Create each possible combination per overlap and add it as an edge.
        for courses in list_of_overlaps:
            for pair in itertools.combinations(courses, 2):
                network.add_edge(pair[0], pair[1])

        # Gather the data that was generated inside the graph.
        course_conflicts = {}
        for course_name in list(network.nodes):
            course_conflicts[course_name] = sorted(list(network[course_name].keys()))

        # Assign the corresponding conflicting courses to each course.
        for course in self.courses:
            course.set_conflicting_courses(course_conflicts[course.name])

    def calculate_saturation_degree_for_unscheduled_event(self, event: Event) -> int:
        """
        Calculate a saturation degree which indicates the total amount of
        timeslot conflicts in the timetable for an unscheduled event.
        """
        saturation_degree = 0

        # Iterate over each timeslot in the timetable and calculate the amount
        # of course conflicts for the given event.
        for day in self.timetable:
            for timeslot in day.values():
                saturation_degree += timeslot.get_saturation_degree_for_course(event.course)

        return saturation_degree

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} events:{len(self.get_events())}>'

    def __iter__(self) -> Generator:
        """
        Allow to iterate over the timetable events.
        """
        for day in self.timetable:
            yield day

    def __getitem__(self, index: int) -> TimetableDay:
        """
        Get an timetable day by index.
        """
        return self.timetable[index]

    def __eq__(self, other) -> bool:
        """
        Check if two timetables are the same class type and schedule.
        """
        if self.__class__ != other.__class__:
            return False

        events = self.get_events()
        other_events = other.get_events()

        if len(events) != len(other_events):
            return False

        return sorted(events) == sorted(other_events)

    def serialize(self) -> list:
        """
        Serialize the data inside this class to a JSON-friendly structure.
        """
        return self.timetable

    def get_events(self) -> list[Event]:
        """
        Get a list with all events in this timetable.
        """
        events = []

        for day in self.timetable:
            for timeslot in day.values():
                for event in timeslot:
                    events.append(event)

        return events

    def register_students_to_courses(self):
        """
        Register all the students to the courses that they signed up for.
        """
        for course in self.courses:
            students = [s for s in self.students if course.name in s.enrolled_courses]
            course.register_students(students)

    def add_event(self, event: Event) -> None:
        """
        Add a single event to the timetable.
        """
        assert event.weekday is not None, 'weekday must be set'
        assert event.timeslot is not None, 'timeslot must be set'

        weekday = self.timetable[event.weekday - 1]

        if event.timeslot not in weekday:
            weekday[event.timeslot] = Timeslot(event.timeslot, event.weekday)

            # Sort the timeslots in ascending order.
            self.timetable[event.weekday - 1] = dict(sorted(weekday.items()))

        weekday[event.timeslot].add_event(event)

    def remove_event(self, event: Event) -> None:
        """
        Remove a single event from the timetable.
        """
        assert event.weekday is not None, 'weekday must be set'
        assert event.timeslot is not None, 'timeslot must be set'

        timeslot = self.timetable[event.weekday - 1][event.timeslot]
        timeslot.remove_event(event)

        if len(timeslot) == 0:
            del self.timetable[event.weekday - 1][event.timeslot]

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

    def calculate_empty_timeslots_malus_score(self) -> int:
        """
        Calculate malus score for the empty timeslots per student timetable.
        """
        score = 0

        student_timetables = self.get_student_timetables()
        for timetable in student_timetables.values():
            for day in timetable:
                timeslots = list(day.values())
                for index, timeslot in enumerate(timeslots):
                    if index == 0:
                        continue

                    prev_timeslot = timeslots[index - 1]
                    total_empty_timeslots = self.get_total_empty_timeslots(timeslot, prev_timeslot)
                    if total_empty_timeslots == 1:
                        score += 1
                    elif total_empty_timeslots == 2:
                        score += 3

        return score

    def calculate_malus_score(self) -> int:
        """
        Calculates the malus score for the timetable.
        The perfect score is 0, anything higher is worse.
        """
        score = 0

        # Get the malus score for each timeslot.
        for day in self.timetable:
            for timeslot in day.values():
                score += timeslot.calculate_malus_score()

        score += self.calculate_empty_timeslots_malus_score()

        return score

    def is_solution(self) -> bool:
        """
        Check if the timetable structure is valid by checking constraints.
        """
        return len(self.get_violations()) == 0 and \
            self.get_total_timeslots() <= self.MAX_TIMESLOTS_PER_WEEK

    def get_events_by_course(self) -> list[list[Event]]:
        """
        Group all events by course.
        """
        course_events = {}

        for day in self.timetable:
            for timeslot in day.values():
                for event in timeslot:
                    if event.course.id not in course_events:
                        course_events[event.course.id] = []
                    course_events[event.course.id].append(event)

        return list(course_events.values())

    def get_student_timetables(self) -> dict[str, TimetableList]:
        """
        Group all events by student is where each key is the student is and the
        value is a personal timetable list.

        Example structure that will be returned:
        {
            <student_id>: [
                { // monday
                    9: Timeslot(events:[Event(), Event()]),
                    11: Timeslot(events:[Event(), Event()]),
                },
                { // tuesday },
                { // wednesday },
                { // thursday },
                { // friday
                    9: Timeslot(events:[Event(), Event()]),
                    11: Timeslot(events:[Event(), Event()]),
                }
            ]
        }
        """
        student_timetables = {}

        # Group all events per student id.
        for day_index, day in enumerate(self.timetable):
            for (hour, timeslot) in day.items():
                for event in timeslot:
                    for student in event.students:
                        if student.student_id not in student_timetables:
                            student_timetables[student.student_id] = self.new_timetable()
                        if hour not in student_timetables[student.student_id][day_index]:
                            student_timetables[student.student_id][day_index][hour] = Timeslot(hour, day_index + 1)
                        if event not in student_timetables[student.student_id][day_index][hour]:
                            student_timetables[student.student_id][day_index][hour].add_event(event)

        # Sort all the dictionaries by key for each day per student.
        for student_id, timetable in student_timetables.items():
            for index, day in enumerate(timetable):
                student_timetables[student_id][index] = dict(sorted(timetable[index].items()))

        return student_timetables

    def get_total_empty_timeslots(self, timeslot: Timeslot, prev_timeslot: Timeslot) -> int:
        """
        Get the total amount of empty timeslots beween two timeslots.
        """
        return int((abs(timeslot.value - prev_timeslot.value) - Timeslot.TIMEFRAME) / Timeslot.TIMEFRAME)

    def get_empty_timeslot_violations(self) -> list[Event]:
        """
        Go through each day of the week and check per student if that day
        contains two events with 3 or more empty timeslots in-between. Mark the
        17-timeslot as a violation.

        NOTE: 1 or 2 empty timeslots is allowed, but adds a malus point, which
        is less severe than having 3 or more.
        """
        violations = []

        student_timetables = self.get_student_timetables()
        for timetable in student_timetables.values():
            for day in timetable:
                timeslots = list(day.values())
                for index, timeslot in enumerate(timeslots):
                    if index == 0:
                        continue

                    # The only time we can have 3 timeslots in-between two
                    # events is when the first timeslot is at 9:00 and second is
                    # at 17:00. As tested, only mark the 17:00 timeslot as a
                    # violation rather than both of them, as this increases the
                    # amount of retries a lot.
                    prev_timeslot = timeslots[index - 1]
                    if self.get_total_empty_timeslots(timeslot, prev_timeslot) >= 3:
                        violations += timeslot.events

        return remove_duplicates(violations)

    def get_violations(self) -> list[Event]:
        """
        Find the events that violate the constraints.
        """
        violations = []

        # Get all the violations for each timeslot.
        for day in self.timetable:
            for timeslot in day.values():
                violations += timeslot.get_violations()

        # Get all violations that contain 3 or more empty timeslots per student.
        violations += self.get_empty_timeslot_violations()

        return remove_duplicates(violations)

    def new_timetable(self) -> TimetableList:
        return [{}, {}, {}, {}, {}]

    def clear(self) -> None:
        """
        Remove all data from the timetable.
        """
        self.timetable = self.new_timetable()

    def get_available_timeslot_rooms(self, timeslot: Timeslot) -> list[Room]:
        """
        Get all the rooms in a certain timeslot that are not booked yet.
        """
        rooms = [room for room in self.rooms]

        if timeslot.value == 17:
            # If there is already an event, then there are no more options.
            if len(timeslot.events) == 1:
                return []
            else:
                # If there is no event, then the largest room is an option.
                return [room for room in rooms if room.is_largest]

        for event in timeslot:
            rooms.remove(event.room)

        return rooms

    def get_malus_score_distribution(self) -> dict[str, int]:
        """
        Returns a dictionary containing how the malus points for this timetable
        is distributed, where the key is the group label and the value is a
        number representing how much malus points were calculated for that
        group, where as a group can be double booked rooms, student conflicts,
        timeslot 17 events and more.
        """
        info = {
            'student tussensloten': self.calculate_empty_timeslots_malus_score(),
            'tijdslot 17': 0,
            'student overlappende vakken': 0,
            'zaal capaciteit': 0,
            'dubbele vak activiteiten': 0,
        }

        for day in self.timetable:
            for timeslot in day.values():
                info['tijdslot 17'] += timeslot.calculate_timeslot_17_malus_score()
                info['student overlappende vakken'] += timeslot.get_overlapping_student_courses_malus_score()
                info['zaal capaciteit'] += timeslot.calculate_room_overfitting_malus_score()
                info['dubbele vak activiteiten'] += timeslot.calculate_duplicate_course_events_malus_score()

        return info

    def export_csv(self, filename: str = 'timetable.csv') -> None:
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
                                event.type.value,
                                Weekdays(event.weekday).name,
                                event.timeslot,
                                event.room.location_id
                            ]

                            rows += 1
                            writer.writerow(row)
            file.close()

        self.logger.info(f'Successfully saved timetable with {rows} records as {filepath}')

    def create_ics_event(self, event: Event) -> ics.Event:
        assert event.weekday is not None, 'weekday must be set'
        assert event.timeslot is not None, 'timeslot must be set'
        assert event.room is not None, 'room must be set'

        now = datetime.now()
        utc_offset = get_utc_offset()
        last_monday = now - timedelta(days=max(now.weekday(), 0))

        # Create a list of dates for the current week from mon-fri.
        current_week_dates = [(last_monday + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(5)]

        # Create the ICS calendar event
        e = ics.Event()
        e.name = event.title
        e.location = event.room.location_id
        e.description = f'Enrolled students: {len(event.students)}'

        today_date = current_week_dates[event.weekday - 1]
        start_time = format(event.timeslot, '02')
        end_time = event.timeslot + 2
        e.begin = datetime.fromisoformat(f'{today_date}T{start_time}:00:00{utc_offset}')
        e.end = datetime.fromisoformat(f'{today_date}T{end_time}:00:00{utc_offset}')

        return e

    def get_events_by_course_per_day(self) -> list[list[list[Event]]]:
        """
        Group all events by course for each day in the timetable.
        Example structure that will be returned:
        [
            [ // monday
                [ // course 1
                    Event(), Event(),
                ],
                ...
                [ // course n
                    Event(), Event(),
                ],
            ],
            ...
            [ // friday
                [ // course 1
                    Event(), Event(),
                ],
                ...
            ]
        ]
        """
        timetable = []

        for day in self.timetable:
            course_events: dict[str, list[Event]] = {}

            for timeslot in day.values():
                for event in timeslot:
                    if event.course.id not in course_events:
                        course_events[event.course.id] = []
                    course_events[event.course.id].append(event)

            timetable.append(list(course_events.values()))

        return timetable

    def export_ics(self, filename: str = 'timetable.ics') -> None:
        """
        Export the timetable to ics format for this week.

        Since the timetable contains 5 days, every export will be for the
        current week. If you're doing an export on Saturday, then you will get
        an export still for that week. This is easy and convenient when
        importing into any calendar application.
        """
        ICS_OUT_DIR = os.path.join(OUT_DIR, 'ics')
        COURSES_OUT_DIR = os.path.join(ICS_OUT_DIR, 'courses')
        STUDENTS_OUT_DIR = os.path.join(ICS_OUT_DIR, 'students')

        for d in [ICS_OUT_DIR, COURSES_OUT_DIR, STUDENTS_OUT_DIR]:
            if not os.path.isdir(d):
                os.mkdir(d)

        # Create the ICS calendar file that contains all events.
        #  =====================================================
        total_events = 0
        calendar = ics.Calendar()
        for day in self.timetable:
            for timeslot in day.values():
                for event in timeslot:
                    total_events += 1
                    calendar.events.add(self.create_ics_event(event))

        filepath = os.path.join(ICS_OUT_DIR, filename)
        with open(filepath, 'w') as file:
            file.write(calendar.serialize())
            file.close()

        self.logger.info(f'Successfully saved timetable with {total_events} events as {filepath}')

        # Create separate ICS calendar files for each student.
        # ===================================================
        student_timetables = self.get_student_timetables()
        for student_id, timetable in student_timetables.items():
            total_events = 0
            calendar = ics.Calendar()
            for day in timetable:
                for timeslot in day.values():
                    for event in timeslot:
                        total_events += 1
                        calendar.events.add(self.create_ics_event(event))

            filepath = os.path.join(STUDENTS_OUT_DIR, f'{student_id}_{filename}')
            with open(filepath, 'w') as file:
                file.write(calendar.serialize())
                file.close()

            self.logger.info(f'Successfully saved timetable for student #{student_id} with {total_events} events as {filepath}')


        # Create separate ICS calendar files for each course and its events.
        # =================================================================
        course_events = self.get_events_by_course()
        for events in course_events:
            total_events = 0
            calendar = ics.Calendar()

            for event in events:
                total_events += 1
                calendar.events.add(self.create_ics_event(event))

            course_name_raw = events[0].course.name
            course_name = re.sub(r'[^a-zA-Z0-9]+', '_', course_name_raw.lower())
            filepath = os.path.join(COURSES_OUT_DIR, f'{course_name}_{filename}')
            with open(filepath, 'w') as file:
                file.write(calendar.serialize())
                file.close()

            self.logger.info(f'Successfully saved timetable for course {course_name_raw} with {total_events} events as {filepath}')

    def export_json(self, filename: str = 'timetable.json') -> None:
        filepath = os.path.join(OUT_DIR, filename)
        with open(filepath, 'w') as file:
            file.write(json.dumps(serialize(copy.deepcopy(self.timetable))))
            file.close()
        self.logger.info(f'Successfully saved timetable as {filepath}')

    def plot_heatmap(self) -> None:
        """
        Plot all the events in the timetable.
        """
        # Create a list of timeslots to be used as the y-axis.
        timeslots = Timeslot.OPTIONS

        # Create a list of days to be used as the x-axis.
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']

        # Create a 2D array of zeros with the same shape as the timetable list.
        events_heatmap = [[0 for _ in range(len(timeslots))] for _ in range(len(days))]
        scores_heatmap = [[0 for _ in range(len(timeslots))] for _ in range(len(days))]

        # Make two plots with 1 row and 3 columns.
        fig, ax = plt.subplots(1, 3, figsize=(20, 6))
        fig.tight_layout(pad=8)
        fig.subplots_adjust(wspace=0.5)

        # Set the super title for the plot.
        fig.suptitle('Timetable')

        for i, day in enumerate(self.timetable):
            for j, timeslot in enumerate(day.values()):
                # Add the malus score for each timeslot.
                scores_heatmap[j][i] = timeslot.calculate_malus_score()
                for event in timeslot:
                    # Add 1 for each event that is scheduled in that timeslot.
                    events_heatmap[j][i] += 1

        total_events = len(self.get_events())
        malus_score = self.calculate_malus_score()

        heatmaps = [
            {
                'title': f'Activiteiten (totaal = {total_events})',
                'heatmap': events_heatmap,
            },
            {
                'title': f'Maluspunten (totaal = {malus_score})',
                'heatmap': scores_heatmap,
            },
        ]
        for index, subplot in enumerate(ax[:2]):
            item = heatmaps[index]
            heatmap = item['heatmap']
            subplot.set_title(item['title'])

            # Create the heatmap.
            subplot.imshow(heatmap, cmap='gray_r',
                           extent=[-0.5, len(days)-0.5, len(timeslots)-0.5, -0.5])

            # Create the x-axis and y-axis ticks.
            subplot.set_xticks(range(len(days)), days)
            subplot.set_yticks(range(len(timeslots)), [f'{t}:00 - {t+2}:00' for t in timeslots])

            # Add the heatmap values inside the timeslots.
            for i in range(len(days)):
                for j in range(len(timeslots)):
                    if heatmap[j][i] != '':
                        subplot.text(i, j, heatmap[j][i], ha='center',
                                     va='center', color='r', fontweight='bold',
                                     fontsize='x-large')

        # Plot a third graph showing the malus points distribution.
        bar_graph = ax[2]
        malus_score_info = self.get_malus_score_distribution()
        x = list(malus_score_info.keys())
        y = list(malus_score_info.values())
        bar_graph.set_xlabel('maluspunten')
        bar_container = bar_graph.barh(x, y, edgecolor='white', color='crimson')
        bar_graph.set_title(f'Maluspunten verdeling (totaal = {malus_score})')

        for i, bar in enumerate(bar_container):
            # Put the bar values on top of the bars.
            bar_graph.text(bar.get_width(), i, y[i], fontweight='bold', va='center', ha='left')

        plt.show()

    def print_debug_info(self) -> None:
        """
        Print debug info, such as malus score calculation for all timeslots.
        """
        debug_info = {}

        for day_index, day in enumerate(self.timetable):
            weekday = day_index + 1
            weekday_name = Weekdays(weekday).name
            debug_info[weekday_name] = {}

            for hour, timeslot in day.items():
                if hour not in debug_info[weekday_name]:
                    debug_info[weekday_name][hour] = {
                        'total_events': len(timeslot.events),
                        'saturation_degree': [],
                        'malus_points': {},
                    }

                info = debug_info[weekday_name][hour]

                # Calculate saturation degrees.
                for event in timeslot:
                    info['saturation_degree'].append({
                        'event_title': event.title,
                        'course_name': event.course.name,
                        'degree': timeslot.get_saturation_degree_for_course(event.course)
                    })

                # Calculate malus points.
                info['malus_points']['timeslot_17'] = timeslot.calculate_timeslot_17_malus_score()
                info['malus_points']['room_fitting'] = timeslot.calculate_room_overfitting_malus_score()
                info['malus_points']['duplicate_course_events'] = timeslot.calculate_duplicate_course_events_malus_score()
                info['malus_points']['overlapping_student_courses'] = timeslot.get_overlapping_student_courses_malus_score()

        # Print it rather than log it, because we use this for debugging only.
        print('---------------------------')
        print('Timetable debug information')
        print('---------------------------')
        print(json.dumps(serialize(debug_info), indent=4))
