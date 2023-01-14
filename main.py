#!/usr/bin/env python3


from code.algorithms.randomizer import Randomizer
from code.utils.statistics import print_algorithm_average_statistics, print_algorithm_info


if __name__ == '__main__':
    randomizer = Randomizer()
    randomizer.run()

    # print_algorithm_average_statistics(randomizer, iterations=5000)

    print_algorithm_info(randomizer)
    if randomizer.timetable.is_valid():
        # randomizer.timetable.export_csv('timetable.csv')
        randomizer.timetable.show_plot()
