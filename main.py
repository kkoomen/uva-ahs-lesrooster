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
    logger.info(f'Valid timetable: {is_valid}')
    logger.info(f'Timetable value: {randomizer.timetable.calculate_value()}')
    logger.info(f'Found {len(randomizer.timetable.get_violations())} violations')

    if is_valid:
        randomizer.timetable.export_csv('timetable.csv')
        randomizer.timetable.show_plot()


if __name__ == '__main__':
    main()
