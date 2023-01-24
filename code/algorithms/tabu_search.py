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

    def mutate_candidate(self, candidate: Timetable) -> None:
        """
        Mutate the timetable with some random actions.

        The actions are as follows:
        - 30% chance to one of the worst events
        - 30% chance to move a single event
        - 30% chance to swap two random events
        - 10% chance to permute students within a course
        """
        n = random.random()
        if n < 0.3:
            self.move_high_malus_score_events(candidate)
        elif 0.3 <= n < 0.6:
            self.move_random_event(candidate)
        elif 0.6 <= n < 0.9:
            self.swap_two_random_events(candidate)
        else:
            self.permute_students_for_random_course(candidate)

    def get_neighbor(self, best_candidate: Timetable) -> Timetable:
        """
        Generate n-neighbor solutions based on a given candidate.
        """
        while True:
            candidate = copy.deepcopy(best_candidate)
            self.mutate_candidate(candidate)
            if candidate.is_solution():
                return candidate

    @timer
    def run(self, iterations: int) -> None:
        max_tabu_list_size = 50
        tenure = 10

        initial_solution: Timetable = self.get_initial_solution()
        best_solution = initial_solution
        tabu_list: list[list] = []
        tabu_list.append([initial_solution, tenure])

        violations = len(initial_solution.get_violations())
        malus_score = initial_solution.calculate_malus_score()
        self.logger.info(f'Initial solution state has {violations} violations and {malus_score} malus score')

        for i in range(iterations):
            if i % 100 == 0 and i > 0:
                self.logger.info(f'Starting iteration {i}/{iterations}')

            candidate = self.get_neighbor(best_solution)

            candidate_score = candidate.calculate_malus_score()
            best_solution_score = best_solution.calculate_malus_score()
            if candidate_score < best_solution_score:
                self.logger.info(f'Found new best solution with {candidate_score} malus score (previous:{best_solution_score})')
                best_solution = candidate
            elif candidate not in tabu_list:
                tabu_list.append([candidate, tenure])
                if len(tabu_list) > max_tabu_list_size:
                    tabu_list.pop(0)

            if best_solution_score == 0:
                self.logger.info('🎉  Found the best solution possible, hooray!')
                break

            # Aspiration criteria: allow tabu items as a new best solution.
            for tabu in tabu_list:
                if tabu[0].calculate_malus_score() < best_solution_score:
                    best_solution = tabu[0]

            # Decrease the tenure.
            for tabu in tabu_list:
                tabu[1] -= 1
                if tabu[1] == 0:
                    tabu_list.remove(tabu)

            tabu_list.append([candidate, tenure])

            self.statistics.append({ 'malus_score': best_solution_score })

        self.timetable = best_solution
