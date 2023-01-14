#!/usr/bin/env python3

import logging

from code.algorithms.randomizer import Randomizer
from code.entities.timetable import Timetable


def main():
    logger = logging.getLogger('global')

    timetable = Timetable()
    randomizer = Randomizer(timetable)
    randomizer.run()

    is_valid = randomizer.timetable.is_valid()
    logger.info('Timetable info:')
    logger.info(f'\tValid: {is_valid}')
    logger.info(f'\tTotal timeslots: {randomizer.timetable.get_total_timeslots()}')
    logger.info(f'\tMalus score: {randomizer.timetable.calculate_malus_score()}')
    logger.info(f'\tViolations amount: {len(randomizer.timetable.get_violations())}')

    if is_valid:
        randomizer.timetable.export_csv('timetable.csv')
        randomizer.timetable.show_plot()


if __name__ == '__main__':
    main()
