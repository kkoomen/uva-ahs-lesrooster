#!/usr/bin/env python3

import argparse
from datetime import datetime
import logging

from code.algorithms.base import Algorithm
from code.algorithms.randomizer import Randomizer
from code.utils.constants import LOG_DIR
from code.utils.statistics import (
    print_algorithm_average_statistics,
    print_algorithm_info,
)


def setup_logging(level='info', quiet=False) -> None:
    """
    Setup logging file and stream logging.
    """
    levels = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.critical,
    }

    today_date = str(datetime.now().date())
    logging.basicConfig(filename=f'{LOG_DIR}/{today_date}.txt',
                        level=levels[level])

    # Add a stream handler if the quiet flag is not set.
    if not quiet:
        console = logging.StreamHandler()
        console.setLevel(levels[level])

        formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')
        console.setFormatter(formatter)

        logging.getLogger('').addHandler(console)

    # Immediately log as an indication that the program has initialized.
    global_logger = logging.getLogger('global')
    global_logger.info('='*45)
    global_logger.info(f'Program started at {str(datetime.now())}')
    global_logger.info('='*45)


def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments and return them.
    """
    parser = argparse.ArgumentParser(
        prog = 'Lesrooster',
        description = 'Generate timetables with different algorithms',
        epilog = 'This program is part of the Algorithms and Heuristics course at the University of Amsterdam.')

    parser.add_argument('-l', '--log-level',
                        choices=['debug', 'info', 'warning', 'error', 'critical'],
                        default='info',
                        help='Set the log level for stdout as well as the logfile.')

    parser.add_argument('-q', '--quiet',
                        action='store_true',
                        help='Hide any output produced by the logger for stdout.')

    parser.add_argument('-a', '--algorithm',
                        choices=['randomizer'],
                        help='Run any of the algorithms of choice.')

    parser.add_argument('-i', '--iterations',
                        type=int,
                        default=1,
                        help='How many times the algorithm should run')

    parser.add_argument('-e', '--export',
                        choices=['csv', 'ics'],
                        help='Export the timetable data to one of the available choices (NOTE: This only works if the amount of iterations is exactly 1)')

    parser.add_argument('-p', '--show-plot',
                        action='store_true',
                        help='Plot data from the selected algorithm (if implemented).')

    return parser.parse_args()


def main():
    """
    The main function that will be executed first in this file.
    """
    args = parse_arguments()

    setup_logging(level=args.log_level, quiet=args.quiet)

    algorithm = None
    if args.algorithm == 'randomizer':
        algorithm = Randomizer()

    if isinstance(algorithm, Algorithm):
        if args.iterations > 1:
            print_algorithm_average_statistics(algorithm, iterations=args.iterations)
        else:
            algorithm.run()
            print_algorithm_info(algorithm)

            if args.export == 'csv':
                algorithm.timetable.export_csv()

            elif args.export == 'ics':
                algorithm.timetable.export_ics()

            if args.show_plot:
                algorithm.timetable.show_plot()


if __name__ == '__main__':
    main()
