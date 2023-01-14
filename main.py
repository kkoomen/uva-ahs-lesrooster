#!/usr/bin/env python3

import logging

from code.algorithms.base import Algorithm
from code.algorithms.randomizer import Randomizer

logger = logging.getLogger('global')

def print_algorithm_average_iterations_statistics(algorithm: Algorithm,
                                                  iterations: int):
    """
    Runs a particular algortihm n-times and prints average statistics.
    """
    total_solutions = 0
    avg_retries = 0
    for _ in range(iterations):
        found_solution, retries = algorithm.run()
        if found_solution:
            total_solutions += 1
        avg_retries += retries
    avg_retries = int(avg_retries / iterations)
    logger.info(f'Average info over {iterations} iterations for algortihm: {algorithm.__class__.__name__}')
    logger.info(f'\tAvg. retries: {avg_retries}')
    logger.info(f'\tSolutions: {total_solutions}/{iterations}')


def print_algorithm_info(algorithm: Algorithm):
    logger.info('Timetable info:')
    logger.info(f'\tValid: {algorithm.timetable.is_valid()}')
    logger.info(f'\tTotal timeslots: {algorithm.timetable.get_total_timeslots()}')
    logger.info(f'\tMalus score: {algorithm.timetable.calculate_malus_score()}')
    logger.info(f'\tViolations amount: {len(algorithm.timetable.get_violations())}')

if __name__ == '__main__':
    randomizer = Randomizer()
    randomizer.run()

    print_algorithm_average_iterations_statistics(randomizer, iterations=10)

    # print_algorithm_info(randomizer)
    # if randomizer.timetable.is_valid():
    #     randomizer.timetable.export_csv('timetable.csv')
    #     randomizer.timetable.show_plot()
