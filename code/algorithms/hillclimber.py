import copy
import logging
import random
from code.algorithms.greedy import RandomGreedy
import matplotlib.pyplot as plt

from code.entities.event import Event
from code.entities.timeslot import Timeslot
from code.entities.timetable import Timetable
from code.utils.enums import Weekdays


class HillClimber(RandomGreedy):
    """
    Hill climber algorithm implementation which grabs a random state and accepts
    it if it is equally good or better than the previous state.
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
        plt.ylabel('# of violations with malus points')

        x = [stat['iteration'] for stat in self.statistics]
        y = [stat['violations'] + stat['malus_score'] for stat in self.statistics]
        plt.plot(x, y)

        lowest_malus_score = min([stat['malus_score'] for stat in self.statistics])
        parent_class_name = self.__class__.__bases__[0].__name__
        plt.title(f'Hill climber based on {parent_class_name} solution (iterations = {max(x)}; malus score = {lowest_malus_score})')
        plt.show()

    def move_random_event(self) -> None:
        """
        Move a single event to another random timeslot.
        """
        events = self.timetable.get_events()
        event = random.choice(events)
        similar_event = self.create_similar_event(event)
        self.timetable.remove_event(event)
        self.timetable.add_event(similar_event)

    def swap_two_random_events(self) -> None:
        """
        Swap two random events with each other.
        """
        events = self.timetable.get_events()
        event = events.pop(random.randrange(len(events)))
        other_event = events.pop(random.randrange(len(events)))
        self.swap_two_events(event, other_event)

    def mutate_state(self) -> None:
        """
        Mutate the timetable with some random actions.

        The actions are as follows:
        - 40% chance to move a single event
        - 40% chance to swap two random events
        - 20% to permute students within a random course
        """
        n = random.random()
        if n < 0.40:
            self.move_random_event()
        elif 0.40 <= n < 0.8:
            self.swap_two_random_events()
        else:
            self.permute_students_for_random_course()

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

            self.mutate_state()

            prev_violations = len(prev_state.get_violations())
            prev_malus_score = prev_state.calculate_malus_score()
            new_violations = len(self.timetable.get_violations())
            new_malus_score = self.timetable.calculate_malus_score()

            # If it is a better solution or at least equally as good
            is_better_solution = (
                new_violations < prev_violations or \
                new_violations == prev_violations and new_malus_score <= prev_malus_score
            )

            is_different_score = (
                new_violations != prev_violations or \
                new_violations == prev_violations and new_malus_score != prev_malus_score
            )

            # Equally good or even better solution.
            if is_better_solution:
                if is_different_score:
                    no_improvement_counter = 0
                    self.logger.info(f'Found better state with {new_violations} violations and {new_malus_score} malus score')
                else:
                    self.logger.debug(f'Found similar state with {new_violations} violations and {new_malus_score} malus score')

                self.statistics.append({
                    'iteration': i + 1,
                    'violations': new_violations,
                    'malus_score': new_malus_score,
                })
            else:
                # Worse solution, reverse changes.
                no_improvement_counter += 1
                self.timetable = prev_state

            prev_state = copy.deepcopy(self.timetable)

        self.logger.info(f'Exceed total iterations')
