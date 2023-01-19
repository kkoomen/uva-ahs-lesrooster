#!/usr/bin/env python3

import argparse
from datetime import datetime
import logging
import matplotlib.pyplot as plt

from code.algorithms.base import Algorithm
from code.algorithms.greedy import Greedy, RandomGreedy
from code.algorithms.hillclimber import HillClimber
from code.algorithms.randomizer import Randomizer
from code.utils.constants import LOG_DIR
from code.utils.statistics import print_algorithm_info


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

    # Set matplotlib log level, because by default it is set to 'debug' which
    # adds a lot of stuff we don't want to we see.
    plt.set_loglevel('error')

    handlers = []

    today_date = str(datetime.now().date())
    handlers.append(logging.FileHandler(f'{LOG_DIR}/{today_date}.txt'))

    # Add a stream handler if the quiet flag is not set.
    if not quiet:
        handlers.append(logging.StreamHandler())

    for handler in handlers:
        handler.setLevel(levels[level])
        formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')
        handler.setFormatter(formatter)

    logging.basicConfig(level=levels[level], handlers=handlers)


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
                        help='Set the log level for stdout as well as the logfile')

    parser.add_argument('-q', '--quiet',
                        action='store_true',
                        help='Hide any output produced by the logger for stdout')

    parser.add_argument('-a', '--algorithm',
                        choices=['random', 'greedy', 'random-greedy', 'hillclimber'],
                        help='Run any of the algorithms of choice')

    parser.add_argument('-e', '--export',
                        choices=['csv', 'ics'],
                        help='Export the timetable data to one of the available choices (NOTE: This only works if the amount of iterations is exactly 1)')

    parser.add_argument('-s', '--plot-stats',
                        action='store_true',
                        help='Plot the statistics after the algorithm has finished running')

    parser.add_argument('--plot-heatmap',
                        action='store_true',
                        help='Plot the timetable heatmap')

    parser.add_argument('-i', '--iterations',
                        type=int,
                        default=1,
                        help='How many times the algorithm should run')

    # -- RANDOM ALGORITHM ARGUMENTS --------------------------------------------
    parser.add_argument('--random-walk',
                        action='store_true',
                        help='Do a random walk and plot the results (random algorithm only)')

    return parser.parse_args()


def main():
    """
    The main function that will be executed first in this file.
    """
    args = parse_arguments()
    setup_logging(level=args.log_level, quiet=args.quiet)

    # Immediately log as an indication that the program has initialized.
    global_logger = logging.getLogger('global')
    global_logger.info('='*45)
    global_logger.info(f'Program started at {str(datetime.now())}')
    global_logger.info('='*45)

    global_logger.info(f'Selected algorithm: {args.algorithm}')

    algorithm = None
    if args.algorithm == 'random':
        algorithm = Randomizer()
    elif args.algorithm == 'greedy':
        algorithm = Greedy()
    elif args.algorithm == 'random-greedy':
        algorithm = RandomGreedy()
    elif args.algorithm == 'hillclimber':
        algorithm = HillClimber()

    assert isinstance(algorithm, Algorithm), 'algorithm must be an instance of Algorithm'

    if isinstance(algorithm, Randomizer) and args.iterations > 1 and args.random_walk:
        algorithm.plot_random_walk(args.iterations)
        return

    algorithm.run(args.iterations)
    print_algorithm_info(algorithm)

    if args.export == 'csv':
        algorithm.timetable.export_csv()
    elif args.export == 'ics':
        algorithm.timetable.export_ics()

    if args.plot_stats:
        algorithm.plot_statistics()

    if args.plot_heatmap:
        algorithm.timetable.show_plot()


if __name__ == '__main__':
    main()
