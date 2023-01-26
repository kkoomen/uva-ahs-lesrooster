from datetime import datetime
from unittest import TestCase, mock

from code.entities.course import Course
from code.entities.event import Event
from code.entities.room import Room
from code.entities.student import Student
from code.entities.timeslot import Timeslot
from code.entities.timetable import Timetable
from code.utils.enums import EventType

def date_in_current_week(date: datetime):
    """
    Check if a given datetime object is within the current week.
    """
    current_year, current_week, _ = datetime.now().isocalendar()
    year, week, _ = date.isocalendar()
    return (current_year, current_week) == (year, week)

class TestTimetable(TestCase):

    @mock.patch('code.utils.data.load_students')
    @mock.patch('code.utils.data.load_courses')
    @mock.patch('code.utils.data.load_rooms')
    def setUp(self, mock_load_rooms, mock_load_courses, mock_load_students):
        # Mock the load_rooms() function.
        self.room1 = Room('C0.110', 5, True)
        self.room2 = Room('C1.04', 2)
        mock_load_rooms.return_value = [self.room1, self.room2]

        # Mock the load_courses() function.
        self.course1 = Course('foo', 1, 0, 0, 0, 0, 5)
        self.course2 = Course('bar', 1, 1, 3, 0, 0, 5)
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

        # Prepare some test events that can be added in each unit test.
        self.event1 = Event('foo lecture 1', EventType.LECTURE, self.course1, 1, 9, self.room1,
                            [self.student1, self.student2, self.student3, self.student4])

        self.event2 = Event('bar lecture 1', EventType.LECTURE, self.course2, 1, 9, self.room2,
                            [self.student1, self.student4])

        self.event3 = Event('bar seminar 1', EventType.SEMINAR, self.course2, 3, 15, self.room2,
                            [self.student4])

        self.event4 = Event('bar seminar 2', EventType.SEMINAR, self.course2, 3, 9, self.room2,
                            [self.student1])

        self.event5 = Event('foo leccture 2', EventType.LECTURE, self.course1, 1, 17, self.room1,
                            [self.student1, self.student2, self.student3, self.student4])

        self.event6 = Event('bar seminar 3', EventType.SEMINAR, self.course1, 3, 15, self.room1,
                            [self.student1, self.student4])

        self.event7 = Event('bar seminar 4', EventType.SEMINAR, self.course1, 4, 9, self.room1,
                            [self.student2])

        self.event8 = Event('bar seminar 4', EventType.SEMINAR, self.course1, 4, 13, self.room1,
                            [self.student2])

        # Set the mocked functions in a certain property that can be accessed by
        # the _new_timetable_instance() to create a new timetable per test.
        self.timetable_args = [mock_load_rooms, mock_load_courses, mock_load_students]

    def _new_timetable_instance(self):
        return Timetable(*self.timetable_args)

    def test_init(self):
        timetable = self._new_timetable_instance()

        self.assertEqual(timetable.rooms, [self.room1, self.room2])
        self.assertEqual(timetable.courses, [self.course1, self.course2])
        self.assertEqual(timetable.students, [self.student1, self.student2, self.student3, self.student4])

        self.assertEqual(timetable.courses[0].enrolled_students, [self.student1, self.student2, self.student3, self.student4])
        self.assertEqual(timetable.courses[1].enrolled_students, [self.student1, self.student4])

        self.assertEqual(timetable.courses[0].conflicting_courses, ['bar'])
        self.assertEqual(timetable.courses[1].conflicting_courses, ['foo'])

    def test_repr(self):
        timetable = self._new_timetable_instance()
        self.assertEqual(repr(timetable), '<Timetable events:0>')

    def test_iter(self):
        timetable = self._new_timetable_instance()
        iterator = iter(timetable)
        self.assertEqual(next(iterator), {})
        self.assertEqual(next(iterator), {})
        self.assertEqual(next(iterator), {})
        self.assertEqual(next(iterator), {})
        self.assertEqual(next(iterator), {})
        self.assertRaises(StopIteration, next, iterator)

    def test_getitem(self):
        timetable = self._new_timetable_instance()
        self.assertEqual(timetable[0], timetable.timetable[0])
        self.assertEqual(timetable[1], timetable.timetable[1])
        self.assertEqual(timetable[2], timetable.timetable[2])
        self.assertEqual(timetable[3], timetable.timetable[3])
        self.assertEqual(timetable[4], timetable.timetable[4])

    def test_eq(self):
        timetable1 = self._new_timetable_instance()
        timetable2 = self._new_timetable_instance()

        self.assertEqual(timetable1 == self.course1, False)
        self.assertEqual(timetable1 == timetable2, True)

        timetable1.add_event(self.event1)
        self.assertEqual(timetable1 == timetable2, False)

        timetable2.add_event(self.event1)
        self.assertEqual(timetable1 == timetable2, True)

    def test_serialize(self):
        timetable = self._new_timetable_instance()

        timetable.add_event(self.event1)
        timetable.add_event(self.event2)
        timetable.add_event(self.event3)

        self.assertEqual(timetable.serialize(), [
            { 9: Timeslot(9, [self.event1, self.event2]) },
            {},
            { 15: Timeslot(15, [self.event3]) },
            {},
            {}
        ])

    def test_get_events(self):
        timetable = self._new_timetable_instance()

        timetable.add_event(self.event1)
        timetable.add_event(self.event2)
        timetable.add_event(self.event3)

        self.assertEqual(timetable.get_events(), [self.event1, self.event2, self.event3])

    def test_add_remove_event(self):
        timetable = self._new_timetable_instance()

        timetable.add_event(self.event1)
        timetable.add_event(self.event2)
        self.assertEqual(timetable.timetable, [{ 9: Timeslot(9, [self.event1, self.event2]) }, {}, {}, {}, {}])
        self.assertEqual(timetable.get_events(), [self.event1, self.event2])

        timetable.remove_event(self.event1)
        self.assertEqual(timetable.timetable, [{ 9: Timeslot(9, [self.event2]) }, {}, {}, {}, {}])
        self.assertEqual(timetable.get_events(), [self.event2])

        timetable.remove_events([self.event2])
        self.assertEqual(timetable.timetable, [{}, {}, {}, {}, {}])
        self.assertEqual(timetable.get_events(), [])

    def test_get_total_timeslots(self):
        timetable = self._new_timetable_instance()
        timetable.add_event(self.event1)
        timetable.add_event(self.event3)
        self.assertEqual(timetable.get_total_timeslots(), 2)

    def test_get_total_empty_timeslots(self):
        timetable = self._new_timetable_instance()
        timetable.add_event(self.event3)
        timetable.add_event(self.event4)
        timeslot1, timeslot2 = timetable.timetable[2].values()
        self.assertEqual(timetable.get_total_empty_timeslots(timeslot1, timeslot2), 2)

    def test_new_timetable(self):
        timetable = self._new_timetable_instance()
        self.assertEqual(timetable.new_timetable(), [{}, {}, {}, {}, {}])

    def test_clear(self):
        timetable = self._new_timetable_instance()
        timetable.add_event(self.event1)
        self.assertEqual(timetable.get_events(), [self.event1])
        self.assertNotEqual(timetable.timetable, [{}, {}, {}, {}, {}])
        timetable.clear()
        self.assertEqual(timetable.get_events(), [])
        self.assertEqual(timetable.timetable, [{}, {}, {}, {}, {}])

    def test_calculate_saturation_degree_for_unscheduled_event(self):
        pass

    def test_get_available_timeslot_rooms(self):
        timetable = self._new_timetable_instance()

        # Check timeslot 17:00 - 19:00.
        timeslot = Timeslot(17)
        self.assertEqual(timetable.get_available_timeslot_rooms(timeslot), [self.room1])
        timeslot.add_event(self.event5)
        self.assertEqual(timetable.get_available_timeslot_rooms(timeslot), [])

        # Check another random timeslot.
        timeslot = Timeslot(9)
        self.assertEqual(timetable.get_available_timeslot_rooms(timeslot), [self.room1, self.room2])
        timeslot.add_event(self.event2)
        self.assertEqual(timetable.get_available_timeslot_rooms(timeslot), [self.room1])

    def test_get_student_timetables(self):
        timetable = self._new_timetable_instance()
        timetable.add_event(self.event1)
        timetable.add_event(self.event2)
        timetable.add_event(self.event3)
        output = {
            '1': [
                { 9: Timeslot(9, [self.event1, self.event2]) },
                {},
                {},
                {},
                {}
            ],
            '2': [
                { 9: Timeslot(9, [self.event1]) },
                {},
                {},
                {},
                {}
            ],
            '3': [
                { 9: Timeslot(9, [self.event1]) },
                {},
                {},
                {},
                {}
            ],
            '4': [
                { 9: Timeslot(9, [self.event1, self.event2]) },
                {},
                { 15: Timeslot(15, [self.event3]) },
                {},
                {}
            ],
        }
        self.assertEqual(timetable.get_student_timetables(), output)

    def test_get_events_by_course(self):
        timetable = self._new_timetable_instance()
        timetable.add_event(self.event1)
        timetable.add_event(self.event2)
        timetable.add_event(self.event3)
        self.assertEqual(timetable.get_events_by_course(), [[self.event1], [self.event2, self.event3]])

    def test_get_empty_timeslot_violations(self):
        timetable = self._new_timetable_instance()
        self.assertEqual(timetable.is_solution(), True)
        timetable.add_event(self.event1)
        timetable.add_event(self.event5)
        self.assertEqual(timetable.get_empty_timeslot_violations(), [self.event5])
        self.assertEqual(timetable.get_violations(), [self.event5])
        self.assertEqual(timetable.is_solution(), False)

    def test_calculate_empty_timeslots_malus_score(self):
        timetable = self._new_timetable_instance()
        timetable.add_event(self.event3)
        timetable.add_event(self.event4)
        timetable.add_event(self.event6)
        timetable.add_event(self.event7)
        timetable.add_event(self.event8)
        self.assertEqual(timetable.calculate_empty_timeslots_malus_score(), 4)
        self.assertEqual(timetable.calculate_malus_score(), 5)

    def test_get_events_by_course_per_day(self):
        timetable = self._new_timetable_instance()
        timetable.add_event(self.event1)
        timetable.add_event(self.event2)
        timetable.add_event(self.event3)
        timetable.add_event(self.event4)
        timetable.add_event(self.event5)
        timetable.add_event(self.event6)
        self.assertEqual(timetable.get_events_by_course_per_day(), [
            [
                [self.event1, self.event5],
                [self.event2],
            ],
            [],
            [
                [self.event4, self.event3],
                [self.event6],
            ],
            [],
            []
        ])

    def test_create_ics_event(self):
        timetable = self._new_timetable_instance()
        ics_event = timetable.create_ics_event(self.event1)
        assert self.event1.room is not None, 'event1 room must bet set'
        self.assertEqual(ics_event.name, self.event1.title)
        self.assertEqual(ics_event.location, self.event1.room.location_id)
        self.assertEqual(ics_event.description, 'Enrolled students: ' + str(len(self.event1.students)))
        self.assertEqual(date_in_current_week(ics_event.begin), True)
        self.assertEqual(date_in_current_week(ics_event.end), True)
