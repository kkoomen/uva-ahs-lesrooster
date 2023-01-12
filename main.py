#!/usr/bin/env python3

import os

from code.algorithms.randomizer import Randomizer
from code.entities.timetable import Timetable
from code.utils.constants import OUT_DIR

# Create the output directory if it doesn't exist yet.
if not os.path.isdir(OUT_DIR):
    os.mkdir(OUT_DIR)


def main():
    timetable = Timetable()
    randomizer = Randomizer(timetable)
    randomizer.run()

    is_valid = randomizer.timetable.is_valid()
    print(f'Valid timetable: {is_valid}')
    print(f'Timetable value: {randomizer.timetable.calculate_value()}')
    print(f'Found {len(randomizer.timetable.get_violations())} violations')

    if is_valid:
        randomizer.timetable.export_csv('timetable.csv', verbose=True)
        randomizer.timetable.show_plot()


if __name__ == '__main__':
    main()
