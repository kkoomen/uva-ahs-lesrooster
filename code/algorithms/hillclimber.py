#!/usr/bin/env python3


import copy
import logging
import random
from code.algorithms.greedy import Greedy
import matplotlib.pyplot as plt

from code.entities.event import Event
from code.entities.timeslot import Timeslot
from code.entities.timetable import Timetable
from code.utils.enums import Weekdays


class HillClimber(Greedy):
    """
    Hill climber algorithm implementation which grabs a random state and accepts
    it if it better than the previous state.
    """

    def __init__(self) -> None:
        self.timetable = Timetable()
        self.logger = logging.getLogger(__name__)
        self.statistics = []

    def create_similar_event(self, event: Event) -> Event:
        """
        Clone the current event, but with other data than the it currently has.
        """
        timeslot = random.choice([n for n in Timeslot.OPTIONS if n != event.timeslot])
        weekday = random.choice([weekday.value for weekday in Weekdays])
        room = random.choice(self.timetable.rooms)
        return Event(event.title, event.type, event.course, weekday, timeslot, room, event.students)

    def move_random_event(self) -> None:
        """
        Move a single event to another random timeslot.
        """
        events = self.timetable.get_events()
        event = random.choice(events)
        self.timetable.remove_event(event)
        similar_event = self.create_similar_event(event)
        self.timetable.add_event(similar_event)

    def generate_state(self) -> None:
        """
        Run the parent algorithm in order to generate a solution.
        """
        super().run()

        # Since this class extends another class, the other class is also
        # keeping track of some statistics, so we have to reset it here.
        self.statistics = []

    def plot_statistics(self) -> None:
        """
        Plot the malus scores during the hill climber process.
        """
        plt.xlabel('# of iterations')
        plt.ylabel('# of malus points')

        x = [stat['iteration'] for stat in self.statistics]
        y = [stat['malus_score'] for stat in self.statistics]
        plt.plot(x, y)

        plt.title(f'Hill climber')
        plt.show()

    def swap_two_random_events(self) -> None:
        """
        Swap two random events with each other.
        """
        events = self.timetable.get_events()
        event = events.pop(random.randrange(len(events)))
        other_event = events.pop(random.randrange(len(events)))
        super().swap_two_events(event, other_event)

    def run(self, iterations=1) -> None:
        """
        Run the hill climber until there are no more improvements.
        """
        self.timetable.clear()
        self.generate_state()

        # Stop if there is no improvement anymore after this amount of times.
        no_improvement_limit = 500

        violations = len(self.timetable.get_violations())
        malus_score = self.timetable.calculate_malus_score()
        self.logger.info(f'Initial solution state has {violations} violations and {malus_score} malus score')

        prev_state = copy.deepcopy(self.timetable)
        no_improvement_counter = 0
        for i in range(iterations):
            if no_improvement_counter == no_improvement_limit:
                self.logger.info(f'Reached local optimum')
                return

            # Log the current iteration every 100 iterations.
            if i % 100 == 0:
                self.logger.debug(f'Starting iteration {i}/{iterations}')

            # 40% chance to move a single event
            # 50% chance to swap two random events
            # 10% to permute students
            n = random.random()
            if n < 0.4:
                self.move_random_event()
            elif 0.4 <= n < 0.9:
                self.swap_two_random_events()
            else:
                self.permute_students()

            # Violations should be checked as they are more important.
            violations = len(self.timetable.get_violations())
            malus_score = self.timetable.calculate_malus_score()
            prev_violations = len(prev_state.get_violations())
            prev_malus_score = prev_state.calculate_malus_score()

            is_better_solution = (
                violations <= prev_violations and \
                malus_score <= prev_malus_score
            )

            if is_better_solution:
                self.statistics.append({
                    'iteration': i + 1,
                    'malus_score': malus_score,
                })
                no_improvement_counter = 0
            else:
                no_improvement_counter += 1
                self.timetable = prev_state

            is_different_state = (
                violations != prev_violations or \
                violations == prev_violations and malus_score != prev_malus_score
            )

            if is_better_solution and is_different_state:
                self.logger.info(f'Found better state with {violations} violations and {malus_score} malus score')
            elif is_better_solution:
                self.logger.debug(f'Found similar state with {violations} violations and {malus_score} malus score')

            prev_state = copy.deepcopy(self.timetable)

        self.logger.info(f'Exceed total iterations')
