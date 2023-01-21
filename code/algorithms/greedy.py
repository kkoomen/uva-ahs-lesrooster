import copy
import logging
import math
import random
from typing import Any
import matplotlib.pyplot as plt

from code.algorithms.base import Algorithm
from code.entities.event import Event
from code.entities.timeslot import Timeslot
from code.entities.timetable import Timetable
from code.utils.enums import EventType
from code.utils.helpers import split_list


class Greedy(Algorithm):
    """
    Constructive greedy algortihm for timetable scheduling.

    NOTE: This will always find the same state with the same malus score.
    """

    def __init__(self):
        self.timetable = Timetable()
        self.logger = logging.getLogger(__name__)
        self.statistics = []

    def plot_statistics(self) -> None:
        """
        Plot the malus scores that we gathered when the algortihm ran.
        """
        plt.xlabel('# of events')
        plt.ylabel('# of malus points per chosen timeslot')

        scores = [stat['malus_score'] for stat in self.statistics]
        total_events = len(scores)
        plt.plot(range(1, total_events + 1), scores)

        plt.title(self.__class__.__name__)
        plt.show()


    def get_unscheduled_events(self) -> list[Event]:
        """
        Create all the events that should be scheduled for each course.
        """
        events = []

        # Sort courses based on the amount of events they will schedule where as
        # the course with the most events to be scheduled is the first one.
        courses = sorted(self.timetable.courses,
                         key=lambda course: course.calculate_total_events(),
                         reverse=True)

        for course in courses:
            # Create the lecture events.
            for _ in range(course.lectures_amount):
                event = Event(f'{course.name} hoorcollege', EventType.LECTURE, course)
                event.assign_students(course.enrolled_students)
                events.append(event)

            # Create the seminar events.
            for _ in range(course.seminars_amount):
                # Create groups based on the seminar capacity and enrolment.
                student_groups, total_groups = course.create_seminar_student_groups()
                for i in range(total_groups):
                    event = Event(f'{course.name} werkcollege', EventType.SEMINAR, course)
                    event.assign_students(student_groups[i])
                    events.append(event)

            # Create the practical events.
            for _ in range(course.practicals_amount):
                # Create groups based on the practicals capacity and enrolment.
                student_groups, total_groups = course.create_seminar_student_groups()
                for i in range(total_groups):
                    event = Event(f'{course.name} practicum', EventType.PRACTICUM, course)
                    event.assign_students(student_groups[i])
                    events.append(event)

        return events

    def get_possibilities(self, event: Event) -> list[dict[str, Any]]:
        """
        Get all the possible states for a certain event.

        This is done by putting the event in each available room in each
        available timeslot in the whole timetable, then calculate the malus
        score for that state and then sort all these states based on the one
        with the least violations and lowest malus score.
        """
        timetable = copy.deepcopy(self.timetable)
        event = copy.deepcopy(event)
        possibilities: list[dict[str, Any]] = []

        # Place the event in each single timeslot and calculate the malus score
        # for that whole timetable state.
        for day_index in range(Timetable.DAYS_PER_WEEK):
            for timeslot_value in Timeslot.OPTIONS:
                day = timetable[day_index]
                timeslot = day[timeslot_value] if timeslot_value in day else None

                # If it is a timeslot, there exists already at least one event
                # in this timeslot.
                if isinstance(timeslot, Timeslot):
                    # Find a suitable room based on the capacity.
                    available_rooms = timetable.get_available_timeslot_rooms(timeslot)
                elif timeslot_value == 17:
                    # Only allow the largest room for the 17:00 timeslot.
                    available_rooms = [room for room in timetable.rooms if room.is_largest]
                else:
                    # Any other timeslot can choose any room.
                    available_rooms = timetable.rooms

                # Remove the removes that are too small for this event.
                suitable_rooms = sorted([room for room in available_rooms if room.capacity >= event.get_capacity()])

                # Continue if there is no available room in this timeslot.
                if len(suitable_rooms) == 0:
                    continue

                room = suitable_rooms[0]
                weekday = day_index + 1

                event.set_weekday(weekday)
                event.set_timeslot(timeslot_value)
                event.set_room(room)

                timetable.add_event(event)
                possibilities.append({
                    'weekday': weekday,
                    'timeslot': timeslot_value,
                    'room': room,
                    'malus_score': timetable.calculate_malus_score(),
                    'total_violations': len(timetable.get_violations())
                })
                timetable.remove_event(event)

        possibilities = sorted(
            possibilities,
            key=lambda possibility: (
                possibility['total_violations'],
                possibility['malus_score'],
                possibility['weekday'],
                possibility['timeslot'],
            )
        )

        return possibilities

    def find_timeslot_possibility(self, event: Event) -> dict[str, Any]:
        """
        Find a possible timeslot for a given event.
        """
        return self.get_possibilities(event).pop(0)

    def get_next_event(self, events: list[Event]) -> Event:
        """
        Get the next item in a list of events.
        """
        return events.pop(0)

    def run(self, iterations=1) -> None:
        """
        Run the algorithm until a solution is found.
        """
        self.logger.info(f'Starting to create timetable')
        self.timetable.clear()

        # Generate events (sort on the amounts of events per course)
        events = self.get_unscheduled_events()

        # While there are events to be scheduled:
        while len(events) > 0:
            # Take the first event
            event = self.get_next_event(events)

            # Get the best possible timeslot option.
            possibility = self.find_timeslot_possibility(event)

            # Schedule the event in the first available possibility
            event.set_weekday(possibility['weekday'])
            event.set_timeslot(possibility['timeslot'])
            event.set_room(possibility['room'])
            self.timetable.add_event(event)

            self.logger.debug(f'Scheduled event "{event.title}" at {event.get_formatted_weekday()}, timeslot {event.timeslot} in room {event.room}')
            self.statistics.append({
                'malus_score': possibility['malus_score']
            })

        self.logger.info(f'Successfully created timetable')

class RandomGreedy(Greedy):
    """
    Random greedy implementation which takes random timeslot possibilites.
    """

    def find_timeslot_possibility(self, event: Event) -> dict[str, Any]:
        """
        Get a random possible timeslot option.
        """
        possibilities = [p for p in self.get_possibilities(event) if p['malus_score'] == 0]
        if len(possibilities) > 0:
            return random.choice(possibilities)
        else:
            return super().find_timeslot_possibility(event)
