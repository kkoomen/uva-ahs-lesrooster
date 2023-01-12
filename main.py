#!/usr/bin/env python3

import os
import random

from code.entities.event import Event
from code.entities.timetable import Timetable
from code.utils.constants import OUT_DIR
from code.utils.data import load_courses, load_rooms, load_students

# Create the output directory if it doesn't exist yet.
if not os.path.isdir(OUT_DIR):
    os.mkdir(OUT_DIR)


def main():
    rooms = load_rooms()
    courses = load_courses()
    students = load_students()

    # Create a timetable with random events and plot it.
    events = 100
    timetable = Timetable()
    for _ in range(events):
        title = random.choice(courses).name
        event_type = random.choice(['hc', 'wc', 'pr'])
        timeslot = random.choice([9, 11, 13, 15, 17])
        room = random.choice(rooms)
        weekday = random.choice([1, 2, 3, 4, 5])
        enrolled_students = random.choices(students, k=random.randint(8, 40))
        event = Event(title, event_type, timeslot, room, weekday, enrolled_students)
        timetable.add_event(event)
    # timetable.show_plot()
    timetable.export_csv('timetable.csv', verbose=True)


if __name__ == '__main__':
    main()
