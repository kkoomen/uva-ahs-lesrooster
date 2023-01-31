import copy
import random
from unittest import TestCase, mock

from code.algorithms.base import Algorithm
from code.entities.course import Course
from code.entities.event import Event
from code.entities.room import Room
from code.entities.student import Student
from code.entities.timetable import Timetable
from code.utils.enums import EventType

class DummyAlgorithm(Algorithm):

    def __init__(self, timetable: Timetable) -> None:
        self.timetable = timetable

    def plot_statistics(self) -> None:
        pass

    def run(self, iterations: int) -> None:
        pass


class TestBaseAlgorithm(TestCase):

    @mock.patch('code.utils.data.load_students')
    @mock.patch('code.utils.data.load_courses')
    @mock.patch('code.utils.data.load_rooms')
    def setUp(self, mock_load_rooms, mock_load_courses, mock_load_students) -> None:
        # Mock the load_rooms() function.
        self.room1 = Room('C0.110', 4, True)
        self.room2 = Room('C1.04', 1)
        mock_load_rooms.return_value = [self.room1, self.room2]

        # Mock the load_courses() function.
        self.course1 = Course('course 1', 1, 2, 3, 0, 0, 4)
        self.course2 = Course('course 2', 1, 0, 0, 0, 0, 2)
        self.course1.set_conflicting_courses(['bar'])
        self.course2.set_conflicting_courses(['foo'])
        mock_load_courses.return_value = [self.course1, self.course2]

        # Mock the load_students() function.
        self.student1 = Student('John', 'Doe', '1', ['foo', 'bar'])
        self.student2 = Student('Mary', 'Jane', '2', ['foo'])
        self.student3 = Student('Mike', 'Smith', '3', ['foo'])
        self.student4 = Student('Steven', 'London', '4', ['bar', 'foo'])
        mock_load_students.return_value = [
            self.student1,
            self.student2,
            self.student3,
            self.student4,
        ]

        # Set the mocked functions in a certain property that can be accessed by
        # the _new_dummy_algorithm() to create a new timetable per test.
        self.timetable_args = [mock_load_rooms, mock_load_courses, mock_load_students]

    def _new_dummy_algorithm(self) -> Algorithm:
        return DummyAlgorithm(Timetable(*self.timetable_args))

    def test_permute_students_for_random_course(self) -> None:
        dummy_algorithm = self._new_dummy_algorithm()

        event1 = Event('foo 1', EventType.SEMINAR, self.course1, 1, 9, self.room1, [self.student1, self.student2])
        event2 = Event('foo 2', EventType.SEMINAR, self.course1, 2, 9, self.room1, [self.student3, self.student4])
        event3 = Event('bar', EventType.PRACTICUM, self.course2, 3, 15, self.room2)

        dummy_algorithm.timetable.add_event(event1)
        dummy_algorithm.timetable.add_event(event2)
        dummy_algorithm.timetable.add_event(event3)

        # Setting the seed to 0 gives us course 2
        random.seed(0)
        dummy_algorithm.permute_students_for_random_course()

        # There should be no change for this course.
        self.assertEqual(event1.students[0] == self.student1, True)
        self.assertEqual(event1.students[1] == self.student2, True)
        self.assertEqual(event2.students[0] == self.student3, True)
        self.assertEqual(event2.students[1] == self.student4, True)

        # Setting the seed to 1 gives us course 1
        random.seed(1)

        dummy_algorithm.permute_students_for_random_course()
        self.assertEqual(event1.students[0] == self.student3, True)
        self.assertEqual(event1.students[1] == self.student1, True)
        self.assertEqual(event2.students[0] == self.student4, True)
        self.assertEqual(event2.students[1] == self.student2, True)

    def test_swap_two_events(self) -> None:
        dummy_algorithm = self._new_dummy_algorithm()

        event1 = Event('foo', EventType.LECTURE, self.course1, 1, 9, self.room1)
        event2 = Event('bar', EventType.PRACTICUM, self.course2, 3, 15, self.room2)

        dummy_algorithm.timetable.add_event(event1)
        dummy_algorithm.timetable.add_event(event2)
        dummy_algorithm.swap_two_events(event1, event2)

        other_event1 = dummy_algorithm.timetable[0][9].events[0]
        other_event2 = dummy_algorithm.timetable[2][15].events[0]

        # Event 1 should have the values of event 2 and vice versa.
        self.assertEqual(other_event1.title, 'bar')
        self.assertEqual(other_event1.type, EventType.PRACTICUM)
        self.assertEqual(other_event1.course, self.course2)

        self.assertEqual(other_event2.title, 'foo')
        self.assertEqual(other_event2.type, EventType.LECTURE)
        self.assertEqual(other_event2.course, self.course1)

        # Do the same, but pass the timetable instance to the function.
        dummy_algorithm.swap_two_events(other_event1, other_event2, dummy_algorithm.timetable)

        other_event1 = dummy_algorithm.timetable[0][9].events[0]
        other_event2 = dummy_algorithm.timetable[2][15].events[0]

        # When swapping again, they should be the same events again.
        self.assertEqual(other_event1 == event1, True)
        self.assertEqual(other_event2 == event2, True)

    def test_swap_two_random_events(self) -> None:
        dummy_algorithm = self._new_dummy_algorithm()

        event1 = Event('foo', EventType.LECTURE, self.course1, 1, 9, self.room1)
        event2 = Event('bar', EventType.PRACTICUM, self.course2, 3, 15, self.room2)

        dummy_algorithm.timetable.add_event(event1)
        dummy_algorithm.timetable.add_event(event2)
        dummy_algorithm.swap_two_random_events()

        other_event1 = dummy_algorithm.timetable[0][9].events[0]
        other_event2 = dummy_algorithm.timetable[2][15].events[0]

        # Event 1 should have the values of event 2 and vice versa.
        self.assertEqual(other_event1.title, 'bar')
        self.assertEqual(other_event1.type, EventType.PRACTICUM)
        self.assertEqual(other_event1.course, self.course2)

        self.assertEqual(other_event2.title, 'foo')
        self.assertEqual(other_event2.type, EventType.LECTURE)
        self.assertEqual(other_event2.course, self.course1)

        # Do the same, but pass the timetable instance to the function.
        dummy_algorithm.swap_two_random_events(dummy_algorithm.timetable)

        other_event1 = dummy_algorithm.timetable[0][9].events[0]
        other_event2 = dummy_algorithm.timetable[2][15].events[0]

        # When swapping again, they should be the same events again.
        self.assertEqual(other_event1 == event1, True)
        self.assertEqual(other_event2 == event2, True)

    def test_create_similar_event(self) -> None:
        """
        We need to check two scenarios:
        - the timeslot is the same as the event timeslot value
        - the timeslot value is different than the event timeslot value

        Using random.seed(2) gives us the timeslot value 9 (same as event var)
        inside the create_similar_event() and then we can later use
        random.seed(0) to get timeslot value 15.
        """
        dummy_algorithm = self._new_dummy_algorithm()
        event = Event('foo', EventType.LECTURE, self.course1, 1, 9, self.room1)

        # No matter the seed value, the new timeslot should always be different
        # from the original timeslot.
        for seed in [2, 0]:
            random.seed(seed)
            new_event = dummy_algorithm.create_similar_event(event)
            is_different_timeslot = (
                new_event.timeslot != event.timeslot and new_event.weekday != event.weekday \
                or \
                new_event.timeslot == 9 and new_event.weekday != event.weekday \
                or \
                new_event.weekday == 1 and new_event.timeslot != event.timeslot
            )
            self.assertEqual(is_different_timeslot, True)

    def test_move_random_event(self) -> None:
        dummy_algorithm = self._new_dummy_algorithm()
        event = Event('foo', EventType.LECTURE, self.course1, 1, 9, self.room1)
        dummy_algorithm.timetable.add_event(event)

        dummy_algorithm.move_random_event()
        other_event = dummy_algorithm.timetable.get_events()[0]

        is_different_timeslot = (
            other_event.timeslot != event.timeslot and other_event.weekday != event.weekday \
            or \
            other_event.timeslot == 9 and other_event.weekday != event.weekday \
            or \
            other_event.weekday == 1 and other_event.timeslot != event.timeslot
        )

        self.assertEqual(is_different_timeslot, True)

    def test_move_high_malus_score_events(self) -> None:
        dummy_algorithm = self._new_dummy_algorithm()

        # Give event 1 a malus score of 1 and event 2 a malus score of 0.
        event1 = Event('foo 1', EventType.LECTURE, self.course1, 1, 9, self.room2, [self.student1, self.student2, self.student3])
        event2 = Event('foo 2', EventType.SEMINAR, self.course2, 2, 9, self.room1, [self.student1])

        dummy_algorithm.timetable.add_event(event1)
        dummy_algorithm.timetable.add_event(event2)

        # Check their malus scores.
        self.assertEqual(dummy_algorithm.timetable.timetable[0][9].calculate_malus_score(), 2)
        self.assertEqual(dummy_algorithm.timetable.timetable[1][9].calculate_malus_score(), 0)

        # This will choose event 1 and swap it with event 2.
        dummy_algorithm.move_high_malus_score_events()

        # After they're swapped, both will have 0 malus points, because swapping
        # also includes rooms and event1 will be put into room 1, which doesn't
        # give any malus points anymore, because all students fit in.
        self.assertEqual(dummy_algorithm.timetable.timetable[0][9].calculate_malus_score(), 0)
        self.assertEqual(dummy_algorithm.timetable.timetable[1][9].calculate_malus_score(), 0)

        other_event1 = dummy_algorithm.timetable.timetable[0][9].events[0]
        other_event2 = dummy_algorithm.timetable.timetable[1][9].events[0]

        # Event 1 should have the values of event 2 and vice versa.
        self.assertEqual(other_event1.title, 'foo 2')
        self.assertEqual(other_event1.type, EventType.SEMINAR)
        self.assertEqual(other_event1.course, self.course2)

        self.assertEqual(other_event2.title, 'foo 1')
        self.assertEqual(other_event2.type, EventType.LECTURE)
        self.assertEqual(other_event2.course, self.course1)

    @mock.patch('random.random')
    def test_mutate_state(self, mock_random) -> None:
        random.seed(0)
        mock_random_values = [0, 0.3, 0.6, 0.9]
        for mock_value in mock_random_values:
            mock_random.return_value = mock_value
            dummy_algorithm = self._new_dummy_algorithm()

            event1 = Event('foo 1', EventType.SEMINAR, self.course1, 1, 9, self.room1, [self.student1, self.student2])
            event2 = Event('foo 2', EventType.SEMINAR, self.course1, 2, 9, self.room2, [self.student3, self.student4])

            dummy_algorithm.timetable.add_event(event1)
            dummy_algorithm.timetable.add_event(event2)

            old_timetable = copy.deepcopy(dummy_algorithm.timetable)
            dummy_algorithm.mutate_state()
            self.assertEqual(dummy_algorithm.timetable != old_timetable, True)
