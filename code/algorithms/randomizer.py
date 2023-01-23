import copy
import logging
import random
from code.utils.decorators import timer
import matplotlib.pyplot as plt

from code.algorithms.base import Algorithm
from code.entities.course import Course
from code.entities.event import Event
from code.entities.timeslot import Timeslot
from code.entities.timetable import Timetable
from code.utils.enums import EventType, Weekdays


class Randomizer(Algorithm):
    """
    This algorithm will create random events in the timetable and reassign any
    of the events that violate the constraints.
    """

    def __init__(self) -> None:
        self.timetable = Timetable()
        self.logger = logging.getLogger(__name__)
        self.statistics = []

    def create_random_event(self, title: str, event_type: EventType, course: Course) -> Event:
        """
        Create an event with a random timeslot, room and weekday.
        """
        timeslot = random.choice(Timeslot.OPTIONS)
        room = random.choice(self.timetable.rooms)
        weekday = random.choice([weekday.value for weekday in Weekdays])
        return Event(title, event_type, course, weekday, timeslot, room)

    def assign_random_events(self) -> None:
        """
        Creates random events based on the courses data.
        """
        courses = copy.deepcopy(self.timetable.courses)
        for _ in range(len(courses)):
            course = courses.pop(random.randrange(len(courses)))
            # Create the lecture events.
            for i in range(course.lectures_amount):
                event = self.create_random_event(f'{course.name} hoorcollege', EventType.LECTURE, course)
                event.assign_students(course.enrolled_students)
                self.timetable.add_event(event)

            # Create the seminar events.
            for _ in range(course.seminars_amount):
                # Create groups based on the seminar capacity and enrolment.
                student_groups, total_groups = course.create_seminar_student_groups(random=True)
                for i in range(total_groups):
                    event = self.create_random_event(f'{course.name} werkcollege', EventType.SEMINAR, course)
                    event.assign_students(student_groups[i])
                    self.timetable.add_event(event)

            # Create the practical events.
            for _ in range(course.practicals_amount):
                # Create groups based on the practicals capacity and enrolment.
                student_groups, total_groups = course.create_practical_student_groups(random=True)
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
        other_events = [e for e in self.timetable.get_events() if e is not event]
        other_event = random.choice(other_events)
        self.swap_two_events(event, other_event)

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

    def plot_statistics(self) -> None:
        """
        Plot the list of retries in a line-graph.
        """
        retries = [stat['retries'] for stat in self.statistics]
        iterations = len(retries)

        plt.xlabel('iterations')
        plt.ylabel('retries')

        plt.plot(range(1, iterations + 1), retries, label='retries')

        average_retries = int(sum(retries) / len(retries))
        plt.axhline(y=average_retries,
                    color='red',
                    linestyle='--',
                    label=f'avg retries ({average_retries})')

        plt.title(f'Timetable (iterations = {iterations})')
        plt.legend()
        plt.show()

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

        self.run()
        assert self.timetable.is_solution(), 'timetable must contain a solution for a random walk'

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
            self.permute_students_for_random_course()
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
            self.permute_students_for_random_course()
            malus_score = self.timetable.calculate_malus_score()
            malus_scores[2]['scores'].append(malus_score)

        self.logger.info(f'[RANDOM WALK] Finished {iterations} iterations event swapping + student permuting')

        # Plot the results
        fig, ax = plt.subplots(len(malus_scores), 1, figsize=(16, 9))
        fig.suptitle(f'Timetable (iterations = {iterations})')
        fig.supxlabel('iterations')
        fig.supylabel('malus points')
        fig.tight_layout(pad=6)

        for index, test_run in enumerate(malus_scores):
            subplot = ax[index]
            subplot.set_yticks([min(test_run['scores']), max(test_run['scores'])])
            subplot.set_title(test_run['label'])
            subplot.plot(range(1, iterations + 1), test_run['scores'])

        plt.show()

    @timer
    def run(self, iterations=1) -> None:
        """
        Assign random events until the timetable is valid.
        """
        for i in range(iterations):
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


            self.statistics.append({
                'iteration': i + 1,
                'retries': retries,
            })
