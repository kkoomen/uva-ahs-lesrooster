import copy
import logging
import math
import random

from code.algorithms.base import Algorithm
from code.entities.course import Course
from code.entities.event import Event
from code.entities.timeslot import Timeslot
from code.entities.timetable import Timetable
from code.utils.enums import EventType, Weekdays
from code.utils.helpers import split_list_random
import matplotlib.pyplot as plt


class Randomizer(Algorithm):
    """
    This algorithm will create random events in the timetable and reassign any
    of the events that violate the constraints.
    """

    def __init__(self) -> None:
        self.timetable = Timetable()
        self.logger = logging.getLogger(__name__)

    def create_random_event(self, title: str, event_type: EventType, course: Course) -> Event:
        """
        Create an event with a random timeslot, room and weekday.
        """
        timeslot = random.choice(Timeslot.OPTIONS)
        room = random.choice(self.timetable.rooms)
        weekday = random.choice([weekday.value for weekday in Weekdays])
        return Event(title, event_type, course, weekday, timeslot, room)

    def create_similar_event(self, event: Event) -> Event:
        """
        Clone the current event, but with other data than the it currently has.
        """
        timeslot = random.choice([n for n in Timeslot.OPTIONS if n != event.timeslot])
        weekday = random.choice([weekday.value for weekday in Weekdays])
        room = random.choice(self.timetable.rooms)
        return Event(event.title, event.type, event.course, weekday, timeslot, room, event.students)

    def assign_random_events(self) -> None:
        """
        Creates random events based on the courses data.
        """
        for course in self.timetable.courses:
            # Create the lecture events.
            for i in range(course.lectures_amount):
                event = self.create_random_event(f'{course.name} hoorcollege', EventType.LECTURE, course)
                event.assign_students(course.enrolled_students)
                self.timetable.add_event(event)

            # Create the seminar events.
            for _ in range(course.seminars_amount):
                # Create groups based on the seminar capacity and enrolment.
                total_groups = math.ceil(course.enrolment / course.seminar_capacity)
                group_capacity = math.ceil(course.enrolment / total_groups)
                student_groups = split_list_random(course.enrolled_students, group_capacity)
                for i in range(total_groups):
                    event = self.create_random_event(f'{course.name} werkcollege', EventType.SEMINAR, course)
                    event.assign_students(student_groups[i])
                    self.timetable.add_event(event)

            # Create the practical events.
            for _ in range(course.practicals_amount):
                # Create groups based on the practicals capacity and enrolment.
                total_groups = math.ceil(course.enrolment / course.practical_capacity)
                group_capacity = math.ceil(course.enrolment / total_groups)
                student_groups = split_list_random(course.enrolled_students, group_capacity)
                for i in range(total_groups):
                    event = self.create_random_event(f'{course.name} practicum', EventType.PRACTICUM, course)
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

    def swap_with_random_event(self, event: Event) -> None:
        """
        Swap a given event with another random event.
        """
        # Gather all other timetable events.
        other_events = []
        for day in self.timetable:
            for timeslot in day.values():
                for e in timeslot:
                    if e is not event:
                        other_events.append(e)

        # Swap the given event with another random event.
        other_event = random.choice(other_events)

        self.timetable.remove_event(event)
        self.timetable.remove_event(other_event)

        new_event = copy.deepcopy(event)
        new_event.set_room(other_event.room)
        new_event.set_weekday(other_event.weekday)
        new_event.set_timeslot(other_event.timeslot)

        other_event.set_room(event.room)
        other_event.set_weekday(event.weekday)
        other_event.set_timeslot(event.timeslot)

        self.timetable.add_event(new_event)
        self.timetable.add_event(other_event)

    def permute_students(self):
        """
        Permute students within the scheduled events inside a course. Seminars
        and practicals may contain 2 or more groups the students will be divided
        over. Students will be permuted within these groups.

        NOTE: Permuting for lectures doesn't make a difference, since it is
        mandatory that all students attend this.
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
            # Only permute among the events if there are 2 or more.
            if len(events) >= 2:
                # Gather all students
                students = [student for event in events for student in event.students]

                # Divide the students in groups
                student_groups = split_list_random(students, len(events))

                # Assign the students to the events
                for i, event in enumerate(events):
                    event.assign_students(student_groups[i])

    def get_random_event(self) -> Event:
        """
        Return a random event from the timetable.
        """
        random_day_index = random.randrange(len(Weekdays))
        day = self.timetable[random_day_index]
        timeslots = [timeslot for timeslot in day.values() if len(timeslot.events) > 0]
        while len(timeslots) == 0:
            random_day_index = random.randrange(len(Weekdays))
            day = self.timetable[random_day_index]
            timeslots = [timeslot for timeslot in day.values() if len(timeslot.events) > 0]

        random_timeslot = random.choice(timeslots)
        return random.choice(random_timeslot.events)


    def plot_iteration_retries(self, retries: list[int]) -> None:
        """
        Plot the list of retries in a line-graph.
        """
        iterations = len(retries)

        plt.xlabel('# of iterations')
        plt.ylabel('# of retries')

        plt.plot(range(1, iterations + 1), retries, label='retries')

        average_retries = int(sum(retries) / len(retries))
        plt.axhline(y=average_retries,
                    color='red',
                    linestyle='--',
                    label=f'avg retries ({average_retries})')

        plt.title(f'Timetable (iterations = {iterations})')
        plt.legend()
        plt.show()

    def print_average_statistics(self, iterations: int) -> None:
        """
        Runs a particular algorithm n-times and prints average statistics.
        """
        retries_list = []
        total_solutions = 0

        min_retries = None
        max_retries = None
        avg_retries = 0

        min_malus_score = None
        max_malus_score = None
        avg_malus_score = 0

        for i in range(iterations):
            self.logger.info(f'Starting iteration {i + 1}/{iterations}')
            found_solution, retries = self.run()
            malus_score = self.timetable.calculate_malus_score()
            retries_list.append(retries)

            if found_solution:
                total_solutions += 1

            # Calculate malus score statistics
            avg_malus_score += malus_score

            if min_malus_score is None or malus_score < min_malus_score:
                min_malus_score = malus_score

            if max_malus_score is None or malus_score > max_malus_score:
                max_malus_score = malus_score


            # Calculate retries statistics
            avg_retries += retries

            if min_retries is None or retries < min_retries:
                min_retries = retries

            if max_retries is None or retries > max_retries:
                max_retries = retries

        avg_retries = int(avg_retries / iterations)
        avg_malus_score = int(avg_malus_score / iterations)

        self.logger.info(f'Average info over {iterations} iterations for {self.__class__.__name__} algorithm:')
        self.logger.info(f'  - Min. retries: {min_retries}')
        self.logger.info(f'  - Max. retries: {max_retries}')
        self.logger.info(f'  - Avg. retries: {avg_retries}')
        self.logger.info(f'  - Min. malus score: {min_malus_score}')
        self.logger.info(f'  - Max. malus score: {max_malus_score}')
        self.logger.info(f'  - Avg malus score: {avg_malus_score}')
        self.logger.info(f'  - Solutions: {total_solutions}/{iterations}')

        self.plot_iteration_retries(retries_list)

    def plot_random_walk(self, iterations: int) -> None:
        """
        Create a single solution and then for n-iterations start doing single
        changes that have influence on the hard constraints to see how the malus
        score will react to these changes.

        In case of the timetable, the following adjustments will be done:
        - swap two random events
        - permute students within a course
        """
        malus_scores = [
            {
                'label': 'Event swapping',
                'scores': [],
            },
            {
                'label': 'Students permuting',
                'scores': [],
            },
            {
                'label': 'Event swapping + students permuting',
                'scores': [],
            },
        ]

        is_solution = self.run()
        if not is_solution:
            self.logger.error('Failed to create solution for random walk')

        timetable_state = copy.deepcopy(self.timetable)

        # Put the current timetable malus score in all the results
        for item in malus_scores:
            malus_score = self.timetable.calculate_malus_score()
            item['scores'].append(malus_score)

        # Swap two random events.
        # ======================
        for _ in range(iterations - 1):
            random_event = self.get_random_event()
            self.swap_with_random_event(random_event)
            malus_score = self.timetable.calculate_malus_score()
            malus_scores[0]['scores'].append(malus_score)

        self.logger.info(f'[RANDOM WALK] Finished {iterations} iterations for event swapping')

        # Permute students.
        # ================
        self.timetable = timetable_state
        timetable_state = copy.deepcopy(self.timetable)
        for _ in range(iterations - 1):
            self.permute_students()
            malus_score = self.timetable.calculate_malus_score()
            malus_scores[1]['scores'].append(malus_score)

        self.logger.info(f'[RANDOM WALK] Finished {iterations} iterations for student permuting')

        # Swap two random events and permute students.
        # ============================================
        self.timetable = timetable_state
        timetable_state = copy.deepcopy(self.timetable)
        for _ in range(iterations - 1):
            random_event = self.get_random_event()
            self.swap_with_random_event(random_event)
            self.permute_students()
            malus_score = self.timetable.calculate_malus_score()
            malus_scores[2]['scores'].append(malus_score)

        self.logger.info(f'[RANDOM WALK] Finished {iterations} iterations event swapping + student permuting')

        # Plot the results
        fig, ax = plt.subplots(len(malus_scores), 1)
        fig.suptitle(f'Timetable (iterations = {iterations})')
        fig.supxlabel('# of iterations')
        fig.supylabel('# of malus points')
        fig.tight_layout(pad=0.75)

        for index, test_run in enumerate(malus_scores):
            subplot = ax[index]
            subplot.set_yticks([min(test_run['scores']), max(test_run['scores'])])
            subplot.set_title(test_run['label'])
            subplot.plot(range(1, iterations + 1), test_run['scores'])

        plt.show()

    def plot_statistics(self) -> None:
        pass

    def run(self) -> tuple[bool, int]:
        """
        Assign random events until the timetable is valid.
        """
        self.timetable.clear()
        self.assign_random_events()
        violations = self.timetable.get_violations()

        max_retries = 1000
        found_solution = True
        retries = 0
        while len(violations) > 0:
            retries += 1

            self.logger.debug(f'[RETRY #{retries}] Found {len(violations)} violations, going to reassign them...')

            # Sometimes it might run into an infinite loop, so stop trying if
            # the retries is above a certain threshold.
            if retries >= max_retries:
                found_solution = False
                break

            self.reassign_events(violations)
            violations = self.timetable.get_violations()

        if found_solution:
            self.logger.info(f'Successfully created random timetable (retries:{retries})')
        else:
            self.logger.info(f'Failed to create random timetable, exceeded max retries (retries:{retries})')

        return found_solution, retries
