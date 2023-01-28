import copy
import logging
import random
from typing import Union
from code.algorithms.base import Algorithm
from code.algorithms.greedy import GreedyLSD
from code.utils.decorators import timer
import matplotlib.pyplot as plt

from code.entities.timetable import Timetable


class HillClimber(Algorithm):
    """
    Hill climber algorithm implementation which grabs a random state and accepts
    it if it is equally good or better than the previous state.
    """

    def __init__(self, algorithm: Union[Algorithm, None]=None) -> None:
        self.timetable = Timetable()
        self.algorithm = algorithm if algorithm is not None else GreedyLSD()
        self.logger = logging.getLogger(__name__)
        self.statistics = []

    def generate_state(self) -> None:
        """
        Run the parent algorithm in order to generate a solution.
        """
        self.algorithm.run(1)
        self.timetable = self.algorithm.timetable

        # Since this class extends another class, the other class is also
        # keeping track of some statistics, so we have to reset it here.
        self.statistics = []

    def plot_statistics(self) -> None:
        """
        Plot the malus scores during the hill climber process.
        """
        plt.xlabel('iterations')
        plt.ylabel('malus points')

        iterations = len(self.statistics)
        x = range(1, iterations + 1)
        y = [stat['malus_score'] for stat in self.statistics]
        plt.plot(x, y)

        lowest_malus_score = min([stat['malus_score'] for stat in self.statistics])
        base_algorithm_name = self.algorithm.__class__.__name__
        plt.title(f'Hill climber using {base_algorithm_name} (iterations = {iterations}; malus score = {lowest_malus_score})')
        plt.show()

    @timer
    def run(self, iterations=1) -> None:
        """
        Run the hill climber for n-iterations until a local optimum is reached.
        """
        self.timetable.clear()
        self.generate_state()

        # Stop if there is no improvement anymore after this amount of times.
        no_improvement_limit = 10000

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
            if i % 100 == 0 and i > 0:
                self.logger.info(f'Starting iteration {max(i, 1)}/{iterations}')

            self.mutate_state()

            prev_violations = len(prev_state.get_violations())
            prev_malus_score = prev_state.calculate_malus_score()
            new_violations = len(self.timetable.get_violations())
            new_malus_score = self.timetable.calculate_malus_score()

            if new_violations == 0 and new_malus_score == 0:
                self.logger.info('🎉  Found the best solution possible, hooray!')
                break

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
                    'malus_score': new_malus_score,
                })
            else:
                # Worse solution, reverse changes.
                no_improvement_counter += 1
                self.timetable = prev_state

                if len(self.statistics) > 0:
                    # If there is no change, just copy the previous stats.
                    self.statistics.append(self.statistics[-1])
                else:
                    # If there is no statistics yet, add one.
                    self.statistics.append({
                        'iteration': i + 1,
                        'malus_score': prev_malus_score,
                    })

            prev_state = copy.deepcopy(self.timetable)

        self.logger.info(f'Exceed total iterations')
