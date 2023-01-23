import copy
import logging
import random
from typing import Any
from code.entities.course import Course
from code.utils.decorators import timer
import matplotlib.pyplot as plt

from code.algorithms.base import Algorithm
from code.entities.event import Event
from code.entities.timeslot import Timeslot
from code.entities.timetable import Timetable
from code.utils.enums import EventType


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
        plt.xlabel('events')
        plt.ylabel('malus points per chosen timeslot')

        scores = [stat['malus_score'] for stat in self.statistics]
        total_events = len(scores)
        plt.plot(range(1, total_events + 1), scores)

        plt.title(self.__class__.__name__)
        plt.show()

    def get_courses(self) -> list[Course]:
        """
        Get courses based on the amount of events they will schedule where as
        the course with the most events to be scheduled is the first one.
        """
        return sorted(self.timetable.courses,
                      key=lambda course: course.calculate_total_events(),
                      reverse=True)

    def get_unscheduled_events(self) -> list[Event]:
        """
        Create all the events that should be scheduled for each course.
        """
        events = []

        for course in self.get_courses():
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
                student_groups, total_groups = course.create_practical_student_groups()
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
                    'total_violations': len(timetable.get_violations()),
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

    @timer
    def run(self, iterations=1) -> None:
        """
        Run the algorithm until a solution is found.
        """
        self.logger.info(f'Starting to create timetable')
        self.timetable.clear()

        # Generate events that are to be scheduled.
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
    Random greedy implementation which takes random timeslot possibilities.
    """

    def __init__(self):
        super().__init__()
        self.random_greedy_statistics = []
        self.probability = 1

    def plot_statistics(self) -> None:
        plt.xlabel('% random probability')
        plt.ylabel('malus points')

        x = [stat['probability'] for stat in self.random_greedy_statistics]
        y = [stat['malus_score'] for stat in self.random_greedy_statistics]
        plt.plot(x, y)

        plt.title(self.__class__.__name__)
        plt.show()

    def get_next_event(self, events: list[Event]) -> Event:
        if random.random() < self.probability:
            return events.pop(random.randrange(len(events)))
        else:
            return super().get_next_event(events)

    def run(self, iterations=1) -> None:
        for prob in range(0, 101, 10):
            self.probability = prob
            super().run(iterations)
            self.random_greedy_statistics.append({
                'probability': prob,
                'malus_score': self.timetable.calculate_malus_score()
            })

class GreedyLSD(Greedy):
    """
    Greedy algorithm with Least Saturation Degree (LSD).
    """

    def get_courses(self) -> list[Course]:
        return self.timetable.courses

    def get_next_event(self, events: list[Event]) -> Event:
        """
        Group the events by their saturation degree and take a random choice
        from those with the highest degree, thus scheduling the events with
        fewer feasible slots as early as possible.
        """
        grouped_events = {}

        # Group all the events by saturation degree.
        for event in events:
            saturation_degree = self.timetable.calculate_saturation_degree_for_unscheduled_event(event)

            if saturation_degree not in grouped_events:
                grouped_events[saturation_degree] = []

            grouped_events[saturation_degree].append(event)

        # Get the highest amount of conflicts.
        highest_degree = max(grouped_events.keys())

        # Sort by the total events a course has to schedule within the group of
        # events with the highest conflict.
        events_group = sorted(grouped_events[highest_degree],
                              key=lambda event: event.course.calculate_total_events())

        event = events_group[0]
        return events.pop(events.index(event))
