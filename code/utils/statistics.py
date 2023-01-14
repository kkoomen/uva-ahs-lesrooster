import logging

from code.algorithms.base import Algorithm

logger = logging.getLogger('global')


def print_algorithm_average_statistics(algorithm: Algorithm,
                                                  iterations: int):
    """
    Runs a particular algorithm n-times and prints average statistics.
    """
    total_solutions = 0
    min_retries = None
    max_retries = None
    avg_retries = 0
    for _ in range(iterations):
        found_solution, retries = algorithm.run()
        avg_retries += retries

        if min_retries is None:
            min_retries = retries
        elif retries < min_retries:
            min_retries = retries

        if max_retries is None:
            max_retries = retries
        elif retries > max_retries:
            max_retries = retries

        if found_solution:
            total_solutions += 1

    avg_retries = int(avg_retries / iterations)

    logger.info(f'Average info over {iterations} iterations for algorithm: {algorithm.__class__.__name__}')
    logger.info(f'\tMin. retries: {min_retries}')
    logger.info(f'\tMax. retries: {max_retries}')
    logger.info(f'\tAvg. retries: {avg_retries}')
    logger.info(f'\tSolutions: {total_solutions}/{iterations}')


def print_algorithm_info(algorithm: Algorithm):
    """
    Print statistics for an algorithm that has been executed.
    """
    logger.info('Timetable info:')
    logger.info(f'\tValid: {algorithm.timetable.is_valid()}')
    logger.info(f'\tTotal timeslots: {algorithm.timetable.get_total_timeslots()}')
    logger.info(f'\tMalus score: {algorithm.timetable.calculate_malus_score()}')
    logger.info(f'\tViolations amount: {len(algorithm.timetable.get_violations())}')
