import copy
import logging
import random
from typing import Union
from code.utils.decorators import timer
import matplotlib.pyplot as plt

from code.algorithms.greedy import GreedyLSD
from code.algorithms.base import Algorithm
from code.entities.timetable import Timetable


class TabuSearch(Algorithm):
    """
    Tabu search algorithm implementation.
    """

    def __init__(self, algorithm: Union[Algorithm, None]=None) -> None:
        self.logger = logging.getLogger(__name__)
        self.algorithm = algorithm if algorithm is not None else GreedyLSD()
        self.statistics = []

    def plot_statistics(self) -> None:
        """
        Plot the malus scores during the tabu search process.
        """
        iterations = len(self.statistics)
        plt.xlabel('iterations')
        plt.ylabel('malus points')

        x = range(1, iterations + 1)
        y = [stat['malus_score'] for stat in self.statistics]
        plt.plot(x, y)

        base_algorithm_name = self.algorithm.__class__.__name__
        plt.title(f'TabuSearch based on {base_algorithm_name} (iterations = {iterations}; malus score = {min(y)})')
        plt.show()

    def get_initial_solution(self) -> Timetable:
        """
        Generate a solution using any of the already implemented algorithms.
        """
        self.algorithm.run(1)
        return self.algorithm.timetable

    def get_neighbor(self, best_candidate: Timetable) -> Timetable:
        """
        Generate n-neighbor solutions based on a given candidate.
        """
        while True:
            candidate = copy.deepcopy(best_candidate)
            self.mutate_state(candidate)
            if candidate.is_solution():
                return candidate

    @timer
    def run(self, iterations: int) -> None:
        """
        Run the tabu search for n-iterations
        """
        max_tabu_list_size = 10000

        initial_solution: Timetable = self.get_initial_solution()
        best_solution = initial_solution
        tabu_list: set[int] = set()

        violations = len(initial_solution.get_violations())
        malus_score = initial_solution.calculate_malus_score()
        self.logger.info(f'Initial solution state has {violations} violations and {malus_score} malus score')

        tabu_list.add(malus_score)

        for i in range(iterations):
            # Log the current iteration every 100 iterations.
            if i % 100 == 0 and i > 0:
                self.logger.info(f'Starting iteration {max(i, 1)}/{iterations}')

            candidate = self.get_neighbor(best_solution)

            candidate_score = candidate.calculate_malus_score()
            best_solution_score = best_solution.calculate_malus_score()

            if candidate_score < best_solution_score:
                self.logger.info(f'Found new best solution with {candidate_score} malus score (previous:{best_solution_score})')
                best_solution = candidate
            elif candidate_score not in tabu_list:
                tabu_list.add(candidate_score)
                if len(tabu_list) > max_tabu_list_size:
                    tabu_list.pop()

            self.statistics.append({ 'malus_score': best_solution_score })

            if best_solution_score == 0:
                self.logger.info('🎉  Found the best solution possible, hooray!')
                break

        self.timetable = best_solution
