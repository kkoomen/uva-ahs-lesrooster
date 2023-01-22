import copy
import logging
import random
import concurrent.futures
from code.utils.decorators import timer
import matplotlib.pyplot as plt

from code.algorithms.greedy import Greedy
from code.algorithms.base import Algorithm
from code.entities.timetable import Timetable


class TabuSearch(Algorithm):
    """
    Tabu search algorithm implementation.
    """

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.statistics = []

    def plot_statistics(self) -> None:
        """
        Plot the malus scores during the tabu search process.
        """
        iterations = len(self.statistics)
        plt.xlabel('# of iterations')
        plt.ylabel('# of malus points')

        x = range(1, iterations + 1)
        y = [stat['malus_score'] for stat in self.statistics]
        plt.plot(x, y)

        plt.title(f'TabuSearch (iterations = {iterations}; malus score = {min(y)})')
        plt.show()

    def get_initial_solution(self) -> Timetable:
        """
        Generate a solution using any of the already implemented algorithms.
        """
        algorithm: Algorithm = Greedy()
        algorithm.run()
        return algorithm.timetable

    def mutate_candidate(self, candidate: Timetable) -> None:
        """
        Mutate the timetable with some random actions.

        The actions are as follows:
        - 40% chance to move a single event
        - 40% chance to swap two random events
        - 10% to permute all students in a random course
        - 10% to a single student in a random course
        """
        n = random.random()
        if n < 0.40:
            self.move_random_event(candidate)
        elif 0.40 <= n < 0.8:
            self.swap_two_random_events(candidate)
        else:
            self.permute_students_for_random_course(candidate)

    def get_neighbors(self, best_candidate: Timetable, n=20) -> list[Timetable]:
        """
        Generate n-neighbor solutions based on a given candidate.
        """
        neighbors: list[Timetable] = []

        while n > 0:
            with concurrent.futures.ThreadPoolExecutor(max_workers=n) as executor:
                def worker():
                    candidate = copy.deepcopy(best_candidate)
                    self.mutate_candidate(candidate)
                    return candidate

                results  = []
                for _ in range(n):
                    results.append(executor.submit(worker))

                # Wait for all the workers to complete.
                concurrent.futures.wait(results)

                # Check if we got any solutions.
                for future in results:
                    candidate = future.result()
                    if candidate.is_solution():
                        neighbors.append(candidate)
                        n -= 1

        return neighbors

    @timer
    def run(self, iterations: int) -> None:
        max_tabu_list_size = 10
        tenure = 10

        initial_solution: Timetable = self.get_initial_solution()
        best_solution = initial_solution
        best_candidate = initial_solution
        tabu_list: list[list] = []
        tabu_list.append([initial_solution, tenure])

        for i in range(iterations):
            self.logger.debug(f'iteration #{i + 1}')

            neighborhood = self.get_neighbors(best_candidate)
            best_candidate = neighborhood[0]

            for candidate in neighborhood:
                if candidate not in tabu_list and candidate.calculate_malus_score() < best_candidate.calculate_malus_score():
                    best_candidate = candidate

            best_candidate_score = best_candidate.calculate_malus_score()
            best_solution_score = best_solution.calculate_malus_score()
            if best_candidate_score < best_solution_score:
                self.logger.info(f'Found new best solution with {best_candidate_score} malus score (previous:{best_solution_score})')
                best_solution = best_candidate

            for index, tabu in enumerate(tabu_list):
                if tabu[0].calculate_malus_score() < best_solution.calculate_malus_score():
                    best_solution = tabu[0]
                    tabu_list.pop(index)
                    break

            if best_solution_score == 0:
                self.logger.info('🎉  Found the best solution possible, hooray!')
                break

            for tabu in tabu_list:
                tabu[1] -= 1
                if tabu[1] == 0:
                    tabu_list.remove(tabu)

            tabu_list.append([best_candidate, tenure])

            if len(tabu_list) > max_tabu_list_size:
                tabu_list.pop(0)

            self.statistics.append({ 'malus_score': best_solution_score })

        self.timetable = best_solution
