from unittest import TestCase
from code.entities.course import Course

from code.entities.event import Event
from code.entities.room import Room
from code.entities.student import Student
from code.utils.enums import EventType

class TestEvent(TestCase):

    def test_init(self):
        course = Course('foo', 1, 2, 10, 0, 0, 22)
        room = Room('C0.110', 50)
        event = Event('foo', EventType.LECTURE, course, 1, 9, room)
        self.assertEqual(isinstance(event.id, int), True)
        self.assertEqual(len(str(event.id)) > 0, True)
        self.assertEqual(event.title, 'foo')
        self.assertEqual(event.type, EventType.LECTURE)
        self.assertEqual(event.course, course)
        self.assertEqual(event.weekday, 1)
        self.assertEqual(event.timeslot, 9)
        self.assertEqual(event.room, room)
        self.assertEqual(event.students, [])

    def test_lt(self):
        course = Course('foo', 1, 2, 10, 0, 0, 22)

        # check if event1 is less than event2 based on weekday.
        event1 = Event('foo', EventType.LECTURE, course, 1, 9, Room('C0.110', 50))
        event2 = Event('foo', EventType.LECTURE, course, 2, 9, Room('C0.110', 50))
        self.assertEqual(event1 < event2, True)

        # check if event3 is less than event4 based on timeslot if they're on
        # the same day.
        event3 = Event('foo', EventType.LECTURE, course, 1, 9, Room('C0.110', 50))
        event4 = Event('foo', EventType.LECTURE, course, 1, 11, Room('C0.110', 50))
        self.assertEqual(event3 < event4, True)

        # check if event5 is less than event6 based on room capacity, which
        # is only added for the sake of ordering a list of events in a timeslot.
        event5 = Event('foo', EventType.LECTURE, course, 1, 9, Room('C1.80', 40))
        event6 = Event('foo', EventType.LECTURE, course, 1, 9, Room('C0.110', 50))
        self.assertEqual(event5 < event6, True)

    def test_sorting(self):
        course = Course('foo', 1, 2, 10, 0, 0, 22)
        event1 = Event('foo 1', EventType.LECTURE, course, 2, 9, Room('C1.08', 50))
        event2 = Event('foo 2', EventType.LECTURE, course, 1, 11, Room('C1.12', 50))
        event3 = Event('foo 3', EventType.LECTURE, course, 1, 9, Room('C1.13', 50))
        event4 = Event('foo 4', EventType.LECTURE, course, 1, 9, Room('C1.04', 30))
        self.assertEqual(sorted([event1, event2, event3, event4]) == [event4, event3, event2, event1], True)

    def test_eq(self):
        course = Course('foo', 1, 2, 10, 0, 0, 22)
        event1 = Event('foo 1', EventType.LECTURE, course, 2, 9, Room('C1.08', 50))
        event2 = Event('foo 2', EventType.LECTURE, course, 1, 11, Room('C1.12', 50))
        self.assertEqual(event1 == event2, False)
        self.assertEqual(event1 == event1, True)

    def test_add_student(self):
        event = Event('foo', EventType.LECTURE, Course('bar', 1, 2, 10, 0, 0, 22), 1, 9, Room('C1.08', 50))
        self.assertEqual(event.students, [])
        student = Student('John', 'Doe', '12345678', ['course1', 'course2'])
        event.add_student(student)
        self.assertEqual(event.students, [student])

    def test_assign_students(self):
        student1 = Student('John', 'Doe', '12345678', ['course1', 'course2'])
        event = Event('foo', EventType.LECTURE, Course('bar', 1, 2, 10, 0, 0, 22), 1, 9, Room('C1.08', 50), [student1])
        self.assertEqual(event.students, [student1])

        student2 = Student('Mary', 'Jane', '12345678', ['course1', 'course2'])
        student3 = Student('Mike', 'Smith', '12345678', ['course1', 'course2'])
        event.assign_students([student2, student3])
        self.assertEqual(event.students, [student2, student3])

    def test_serialize(self):
        event = Event('foo', EventType.LECTURE, Course('bar', 1, 2, 10, 0, 0, 22), 1, 9, Room('C1.08', 50))
        output = {
            'id': event.id,
            'title': 'foo',
            'type': 'hc',
            'course': 'bar',
            'weekday': 1,
            'timeslot': 9,
            'room': 'C1.08',
        }
        self.assertEqual(event.serialize(), output)

    def test_set_room(self):
        room1 = Room('C1.08', 50)
        event = Event('foo', EventType.LECTURE, Course('bar', 1, 2, 10, 0, 0, 22), 1, 9, room1)
        self.assertEqual(event.room, room1)

        room2 = Room('C1.10', 30)
        event.set_room(room2)
        self.assertEqual(event.room, room2)

    def test_set_timeslot(self):
        event = Event('foo', EventType.LECTURE, Course('bar', 1, 2, 10, 0, 0, 22), 1, 9, Room('C1.08', 50))
        self.assertEqual(event.timeslot, 9)
        event.set_timeslot(11)
        self.assertEqual(event.timeslot, 11)

    def test_set_weekday(self):
        event = Event('foo', EventType.LECTURE, Course('bar', 1, 2, 10, 0, 0, 22), 1, 9, Room('C1.08', 50))
        self.assertEqual(event.weekday, 1)
        event.set_weekday(2)
        self.assertEqual(event.weekday, 2)

    def test_get_formatted_weekday(self):
        event = Event('foo', EventType.LECTURE, Course('bar', 1, 2, 10, 0, 0, 22), 1, 9, Room('C1.08', 50))
        self.assertEqual(event.get_formatted_weekday(), 'mon')
        event.set_weekday(2)
        self.assertEqual(event.get_formatted_weekday(), 'tue')
        event.set_weekday(3)
        self.assertEqual(event.get_formatted_weekday(), 'wed')
        event.set_weekday(4)
        self.assertEqual(event.get_formatted_weekday(), 'thu')
        event.set_weekday(5)
        self.assertEqual(event.get_formatted_weekday(), 'fri')

    def test_get_capacity(self):
        course = Course('bar', 1, 2, 10, 0, 0, 22)
        event1 = Event('foo', EventType.LECTURE, course, 1, 9, Room('C1.08', 50))
        event2 = Event('bar', EventType.SEMINAR, course, 2, 9, Room('C1.08', 50))
        event3 = Event('baz', EventType.PRACTICUM, course, 3, 9, Room('C1.08', 50))
        self.assertEqual(event1.get_capacity(), 22)
        self.assertEqual(event2.get_capacity(), 10)
        self.assertEqual(event3.get_capacity(), 0)
