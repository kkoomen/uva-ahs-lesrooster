from unittest import TestCase

from code.entities.course import Course
from code.entities.event import Event
from code.entities.room import Room
from code.entities.student import Student
from code.entities.timeslot import Timeslot
from code.utils.enums import EventType

class TestTimeslot(TestCase):

    def test_init(self) -> None:
        timeslot = Timeslot(9, 1)
        self.assertEqual(timeslot.value, 9)
        self.assertEqual(timeslot.events, [])

    def test_add_remove_event(self) -> None:
        timeslot = Timeslot(9, 1)
        self.assertEqual(timeslot.events, [])
        event = Event('foo', EventType.LECTURE, Course('bar', 1, 2, 10, 0, 0, 22), 1, 9, Room('C1.08', 50))
        timeslot.add_event(event)
        self.assertEqual(timeslot.events, [event])
        timeslot.remove_event(event)
        self.assertEqual(timeslot.events, [])

    def test_get_total_events(self) -> None:
        timeslot = Timeslot(9, 1)
        event1 = Event('foo 1', EventType.LECTURE, Course('bar', 1, 2, 10, 0, 0, 22), 1, 9, Room('C1.08', 50))
        event2 = Event('foo 2', EventType.LECTURE, Course('bar', 1, 2, 10, 0, 0, 22), 2, 9, Room('C1.08', 50))
        event3 = Event('foo 3', EventType.LECTURE, Course('bar', 1, 2, 10, 0, 0, 22), 3, 9, Room('C1.08', 50))
        timeslot.add_event(event1)
        timeslot.add_event(event2)
        timeslot.add_event(event3)
        self.assertEqual(timeslot.get_total_events(), 3)

    def test_iter(self) -> None:
        timeslot = Timeslot(9, 1)
        event1 = Event('foo 1', EventType.LECTURE, Course('bar', 1, 2, 10, 0, 0, 22), 1, 9, Room('C1.08', 50))
        event2 = Event('foo 2', EventType.LECTURE, Course('bar', 1, 2, 10, 0, 0, 22), 2, 9, Room('C1.08', 50))
        event3 = Event('foo 3', EventType.LECTURE, Course('bar', 1, 2, 10, 0, 0, 22), 3, 9, Room('C1.08', 50))
        timeslot.add_event(event1)
        timeslot.add_event(event2)
        timeslot.add_event(event3)
        iterator = iter(timeslot)
        self.assertEqual(next(iterator), event1)
        self.assertEqual(next(iterator), event2)
        self.assertEqual(next(iterator), event3)
        self.assertRaises(StopIteration, next, iterator)

    def test_len(self) -> None:
        timeslot = Timeslot(9, 1)
        event1 = Event('foo 1', EventType.LECTURE, Course('bar', 1, 2, 10, 0, 0, 22), 1, 9, Room('C1.08', 50))
        event2 = Event('foo 2', EventType.LECTURE, Course('bar', 1, 2, 10, 0, 0, 22), 2, 9, Room('C1.08', 50))
        event3 = Event('foo 3', EventType.LECTURE, Course('bar', 1, 2, 10, 0, 0, 22), 3, 9, Room('C1.08', 50))
        timeslot.add_event(event1)
        timeslot.add_event(event2)
        timeslot.add_event(event3)
        self.assertEqual(len(timeslot), 3)

    def test_eq(self) -> None:
        self.assertEqual(Timeslot(9, 1) == Timeslot(9, 1), True)
        self.assertEqual(Timeslot(9, 1) == Timeslot(9, 2), False)
        self.assertEqual(Timeslot(9, 1) == Timeslot(11, 1), False)

    def test_serialize(self) -> None:
        timeslot = Timeslot(9, 1)
        event1 = Event('foo 1', EventType.LECTURE, Course('bar', 1, 2, 10, 0, 0, 22), 1, 9, Room('C1.08', 50))
        event2 = Event('foo 2', EventType.LECTURE, Course('bar', 1, 2, 10, 0, 0, 22), 2, 9, Room('C1.08', 50))
        timeslot.add_event(event1)
        timeslot.add_event(event2)
        self.assertEqual(timeslot.serialize(), [event1, event2])

    def test_get_saturation_degree_for_course(self) -> None:
        timeslot = Timeslot(9, 1)

        course1 = Course('course 1', 1, 2, 10, 0, 0, 22)
        course2 = Course('course 2', 1, 2, 10, 0, 0, 22)
        course3 = Course('course 3', 1, 2, 10, 0, 0, 22)

        course1.set_conflicting_courses(['course 2', 'course 3'])
        course2.set_conflicting_courses(['course 1'])

        event1 = Event('foo 1', EventType.LECTURE, course1, 1, 9, Room('C1.04', 50))
        event2 = Event('foo 2', EventType.LECTURE, course2, 1, 9, Room('C1.08', 30))
        event3 = Event('foo 3', EventType.LECTURE, course3, 1, 9, Room('C1.06', 20))

        timeslot.add_event(event1)
        timeslot.add_event(event2)
        timeslot.add_event(event3)

        self.assertEqual(timeslot.get_saturation_degree_for_course(course1), 2)
        self.assertEqual(timeslot.get_saturation_degree_for_course(course2), 1)
        self.assertEqual(timeslot.get_saturation_degree_for_course(course3), 0)

    def test_get_timeslot_17_violations(self) -> None:
        timeslot = Timeslot(17, 1)

        course = Course('course 1', 1, 2, 10, 0, 0, 22)
        event1 = Event('foo 1', EventType.LECTURE, course, 1, 9, Room('C1.08', 30, True))
        event2 = Event('foo 2', EventType.LECTURE, course, 1, 9, Room('C1.08', 30, True))
        event3 = Event('foo 3', EventType.LECTURE, course, 1, 9, Room('C1.06', 20))

        timeslot.add_event(event1)
        timeslot.add_event(event2)
        timeslot.add_event(event3)

        self.assertEqual(timeslot.get_timeslot_17_violations(), [event2, event3])
        self.assertEqual(timeslot.get_violations(), [event2, event3])

    def test_get_double_booked_violations(self) -> None:
        timeslot = Timeslot(9, 1)

        course = Course('course 1', 1, 2, 10, 0, 0, 22)
        event1 = Event('foo 1', EventType.LECTURE, course, 1, 9, Room('C1.08', 30))
        event2 = Event('foo 2', EventType.LECTURE, course, 1, 9, Room('C1.08', 30))
        event3 = Event('foo 3', EventType.LECTURE, course, 1, 9, Room('C1.06', 20))

        timeslot.add_event(event1)
        timeslot.add_event(event2)
        timeslot.add_event(event3)

        self.assertEqual(timeslot.get_double_booked_violations(), [event2])
        self.assertEqual(timeslot.get_violations(), [event2])

    def test_calculate_room_overfitting_malus_score(self) -> None:
        timeslot = Timeslot(9, 1)
        course = Course('course 1', 1, 2, 10, 0, 0, 22)

        student1 = Student('John', 'Doe', '1', ['course 1'])
        student2 = Student('Mary', 'Jane', '2', ['course 1'])
        student3 = Student('Mike', 'Smith', '3', ['course 1'])
        student4 = Student('Steven', 'London', '4', ['course 1'])

        event = Event('foo', EventType.LECTURE, course, 1, 9, Room('C1.08', 1))
        event.assign_students([student1, student2, student3, student4])
        timeslot.add_event(event)

        self.assertEqual(timeslot.calculate_room_overfitting_malus_score(), 3)
        self.assertEqual(timeslot.calculate_malus_score(), 3)

    def test_calculate_timeslot_17_malus_score(self) -> None:
        timeslot = Timeslot(17, 1)

        course = Course('course 1', 1, 2, 10, 0, 0, 22)
        largest_room = Room('C1.08', 10, True)
        non_largest_room = Room('C1.04', 10)

        event = Event('foo', EventType.LECTURE, course, 1, 9, largest_room)
        timeslot.add_event(event)
        self.assertEqual(timeslot.calculate_timeslot_17_malus_score(), 5)
        self.assertEqual(timeslot.calculate_malus_score(), 5)

        event.set_room(non_largest_room)
        self.assertEqual(timeslot.calculate_timeslot_17_malus_score(), 0)

    def test_calculate_duplicate_course_events_malus_score(self) -> None:
        timeslot = Timeslot(9, 1)

        course = Course('course 1', 1, 2, 10, 0, 0, 22)
        event1 = Event('foo 1', EventType.LECTURE, course, 1, 9, Room('C1.08', 30))
        event2 = Event('foo 2', EventType.SEMINAR, course, 1, 9, Room('C1.06', 35))
        event3 = Event('foo 3', EventType.PRACTICUM, course, 1, 9, Room('C1.04', 20))

        timeslot.add_event(event1)
        timeslot.add_event(event2)
        timeslot.add_event(event3)

        self.assertEqual(timeslot.calculate_duplicate_course_events_malus_score(), 2)
        self.assertEqual(timeslot.calculate_malus_score(), 2)

    def test_get_overlapping_student_courses_malus_score(self) -> None:
        timeslot = Timeslot(9, 1)

        student1 = Student('John', 'Doe', '1', ['course 1'])
        student2 = Student('Mary', 'Jane', '2', ['course 1'])
        student3 = Student('Mike', 'Smith', '3', ['course 1'])

        course1 = Course('course 1', 1, 2, 10, 0, 0, 22)
        course2 = Course('course 2', 1, 2, 10, 0, 0, 22)
        course3 = Course('course 3', 1, 2, 10, 0, 0, 22)

        event1 = Event('foo 1', EventType.LECTURE, course1, 1, 9, Room('C1.08', 30))
        event2 = Event('foo 2', EventType.SEMINAR, course2, 1, 9, Room('C1.06', 35))
        event3 = Event('foo 3', EventType.PRACTICUM, course3, 1, 9, Room('C1.04', 25))

        event1.assign_students([student1, student2])
        event2.assign_students([student3])
        event3.assign_students([student1, student3])

        timeslot.add_event(event1)
        timeslot.add_event(event2)
        timeslot.add_event(event3)

        self.assertEqual(timeslot.get_overlapping_student_courses_malus_score(), 2)
        self.assertEqual(timeslot.calculate_malus_score(), 2)
