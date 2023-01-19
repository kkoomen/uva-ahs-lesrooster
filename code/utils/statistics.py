import logging

from code.algorithms.base import Algorithm

logger = logging.getLogger(__name__)


def print_algorithm_info(algorithm: Algorithm):
    """
    Print statistics for an algorithm that has been executed.
    """
    logger.info('Timetable info:')
    logger.info(f'  - Solution: {algorithm.timetable.is_solution()}')
    logger.info(f'  - Total timeslots: {algorithm.timetable.get_total_timeslots()}')
    logger.info(f'  - Malus score: {algorithm.timetable.calculate_malus_score()}')
    logger.info(f'  - Total violations: {len(algorithm.timetable.get_violations())}')
