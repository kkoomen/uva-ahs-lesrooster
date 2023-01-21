import copy
import logging
import random
from code.algorithms.base import Algorithm
from code.algorithms.greedy import Greedy
from code.algorithms.randomizer import Randomizer
from code.entities.event import Event
from code.entities.timeslot import Timeslot
from code.entities.timetable import Timetable
from code.utils.enums import EventType, Weekdays
from code.utils.helpers import split_list_random


class TabuSearch(Algorithm):
    """
    Tabu search algorithm implementation.
    """

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    def plot_statistics(self) -> None:
        print('TODO')

    def get_initial_solution(self) -> Timetable:
        """
        Generate a solution using any of the already implemented algorithms.
        """
        algorithm: Algorithm = Randomizer()
        algorithm.run()
        return algorithm.timetable

    def create_similar_event(self, timetable: Timetable, event: Event) -> Event:
        """
        Clone the current event, but with other data than the it currently has.
        """
        timeslot = random.choice([n for n in Timeslot.OPTIONS if n != event.timeslot])
        weekday = random.choice([weekday.value for weekday in Weekdays])
        room = random.choice(timetable.rooms)
        return Event(event.title, event.type, event.course, weekday, timeslot, room, event.students)

    def move_random_event(self, timetable: Timetable) -> None:
        """
        Move a single event to another random timeslot.
        """
        events = timetable.get_events()
        event = random.choice(events)
        similar_event = self.create_similar_event(timetable, event)
        timetable.remove_event(event)
        timetable.add_event(similar_event)

    def swap_two_random_events(self, timetable: Timetable) -> None:
        """
        Swap two random events with each other.
        """
        events = timetable.get_events()
        event = events.pop(random.randrange(len(events)))
        other_event = events.pop(random.randrange(len(events)))

        assert event.room is not None, 'event must have a room'
        assert event.weekday is not None, 'event must have a weekday'
        assert event.timeslot is not None, 'event must have a timeslot'

        assert other_event.room is not None, 'other event must have a room'
        assert other_event.weekday is not None, 'other event must have a weekday'
        assert other_event.timeslot is not None, 'other event must have a timeslot'

        timetable.remove_event(event)
        timetable.remove_event(other_event)

        new_event = copy.deepcopy(event)
        new_event.set_room(other_event.room)
        new_event.set_weekday(other_event.weekday)
        new_event.set_timeslot(other_event.timeslot)

        other_new_event = copy.deepcopy(other_event)
        other_new_event.set_room(event.room)
        other_new_event.set_weekday(event.weekday)
        other_new_event.set_timeslot(event.timeslot)

        timetable.add_event(new_event)
        timetable.add_event(other_new_event)

    def permute_students_for_random_course(self, timetable: Timetable) -> None:
        """
        Seminars and practicals may contain 2 or more groups the students will
        be divided over. Students will be permuted within either the seminar
        groups or the practicals for a single random course.
        """
        course = random.choice(timetable.courses)

        # The key will be a course name with the event type, i.e. 'Database wc'.
        # The value is a list of scheduled events for that course type.
        #
        # Example:
        # {
        #   'Databases wc': [Event(), Event(), Event()]
        #   'Databases pr': [Event(), Event()]
        # }
        course_events: dict[str, list[Event]] = {}

        for day in timetable:
            for timeslot in day.values():
                for event in timeslot:
                    if event.type not in course_events:
                        course_events[event.type] = []

                    if event.course == course and event.type != EventType.LECTURE:
                        course_events[event.type].append(event)

        # There might be seminars and practicals, so just choose one.
        selected_type = random.choice(list(course_events.keys()))
        events = course_events[selected_type]

        # Only permute among the events if there are 2 or more.
        if len(events) >= 2:
            # Gather all students.
            students = [student for event in events for student in event.students]

            # Divide the students in groups.
            student_groups = split_list_random(students, len(events))

            # Assign the students to the events.
            for i, event in enumerate(events):
                event.assign_students(student_groups[i])

    def mutate_candiate(self, candidate: Timetable) -> None:
        """
        Mutate the timetable with some random actions.

        The actions are as follows:
        - 40% chance to move a single event
        - 40% chance to swap two random events
        - 20% to permute students within a random course
        """
        n = random.random()
        if n < 0.40:
            self.move_random_event(candidate)
        elif 0.40 <= n < 0.8:
            self.swap_two_random_events(candidate)
        else:
            self.permute_students_for_random_course(candidate)

    def get_neighbors(self, best_candidate: Timetable, n=20) -> list[Timetable]:
        """
        Generate n-neighbor solutions based on a given candidate.
        """
        neighbors: list[Timetable] = []

        while n > 0:
            candidate = copy.deepcopy(best_candidate)
            self.mutate_candiate(candidate)
            if candidate.is_solution() and candidate not in neighbors:
                neighbors.append(candidate)
                n -= 1

        return neighbors

    def run(self, iterations: int) -> None:
        MAX_TABU_LIST_SIZE = 30
        TENURE = 30

        initial_solution: Timetable = self.get_initial_solution()
        best_solution = copy.deepcopy(initial_solution) # sBest ← s0
        best_candidate = copy.deepcopy(initial_solution) # bestCandidate ← s0
        tabu_list: list[list] = [] # tabuList ← []
        tabu_list.append([initial_solution, TENURE]) # tabuList.push(s0)

        # while (not stoppingCondition())
        for i in range(iterations):
            self.logger.debug(f'iteration #{i + 1}')
            neighborhood = self.get_neighbors(best_candidate) # sNeighborhood ← getNeighbors(bestCandidate)
            best_candidate = neighborhood[0] # bestCandidate ← sNeighborhood[0]
            for candidate in neighborhood: # for (sCandidate in sNeighborhood)
                if candidate not in tabu_list and candidate.calculate_malus_score() < best_candidate.calculate_malus_score(): # if ( (not tabuList.contains(sCandidate)) and (fitness(sCandidate) > fitness(bestCandidate)) )
                    best_candidate = candidate # bestCandidate ← sCandidate
            if best_candidate.calculate_malus_score() < best_solution.calculate_malus_score(): # if (fitness(bestCandidate) > fitness(sBest))
                self.logger.debug(f'Found new best solution with {best_candidate.calculate_malus_score()} malus score (previous:{best_solution.calculate_malus_score()})')
                best_solution = best_candidate # sBest ← bestCandidate
            if best_solution.calculate_malus_score() == 0:
                self.logger.info('FOUND THE BEST SOLUTION!!!')
                break
            tabu_list.append([best_candidate, TENURE]) # tabuList.push(bestCandidate)
            for tabu in tabu_list:
                tabu[1] -= 1
                if tabu[1] == 0:
                    tabu_list.remove(tabu)
            if len(tabu_list) > MAX_TABU_LIST_SIZE: # if (tabuList.size > maxTabuSize)
                tabu_list.pop(0) # tabuList.removeFirst()
        # end
        # return sBest
        print("best_solution >>>>", best_solution)
        self.timetable = best_solution
