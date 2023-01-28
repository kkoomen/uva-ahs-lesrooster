from unittest import TestCase

from code.entities.course import Course
from code.entities.student import Student
from code.utils.enums import EventType

class TestCourse(TestCase):

    def test_init(self) -> None:
        course = Course('foo', 1, 2, 10, 0, 0, 22)
        self.assertEqual(isinstance(course.id, int), True)
        self.assertEqual(len(str(course.id)) > 0, True)
        self.assertEqual(course.name, 'foo')
        self.assertEqual(course.lectures_amount, 1)
        self.assertEqual(course.seminars_amount, 2)
        self.assertEqual(course.seminar_capacity, 10)
        self.assertEqual(course.practical_capacity, 0)
        self.assertEqual(course.practicals_amount, 0)
        self.assertEqual(course.enrolment, 22)
        self.assertEqual(course.enrolled_students, [])

    def test_eq(self) -> None:
        course1 = Course('foo', 1, 2, 10, 0, 0, 22)
        course2 = Course('foo', 2, 1, 15, 1, 10, 30)
        self.assertEqual(course1 == course2, False)
        self.assertEqual(course1 == course1, True)

    def test_get_capacity_for_type(self) -> None:
        course = Course('foo', 1, 2, 10, 0, 0, 22)
        self.assertEqual(course.get_capacity_for_type(EventType.LECTURE), 22)
        self.assertEqual(course.get_capacity_for_type(EventType.SEMINAR), 10)
        self.assertEqual(course.get_capacity_for_type(EventType.PRACTICUM), 0)

    def test_register_students(self) -> None:
        course = Course('foo', 1, 2, 10, 0, 0, 22)
        self.assertEqual(len(course.enrolled_students), 0)

        student = Student('John', 'Doe', '1', ['course1', 'course2'])
        course.register_students([student])
        self.assertEqual(len(course.enrolled_students), 1)

    def test_calculate_total_events(self) -> None:
        course = Course('foo', 1, 2, 10, 3, 7, 22)
        self.assertEqual(course.calculate_total_events(), 16)

    def test_create_student_groups(self) -> None:
        enrolled_students = [
            Student('John', 'Doe', '1', ['foo']),
            Student('Mary', 'Jane', '2', ['foo']),
            Student('Mike', 'Smith', '3', ['foo']),
            Student('Steven', 'London', '4', ['foo']),
        ]
        course = Course('foo', 1, 2, 3, 0, 0, 4, enrolled_students)
        groups = course.create_student_groups(3)
        self.assertEqual(len(groups), 2)

    def test_create_seminar_student_groups(self) -> None:
        enrolled_students = [
            Student('John', 'Doe', '1', ['foo']),
            Student('Mary', 'Jane', '2', ['foo']),
            Student('Mike', 'Smith', '3', ['foo']),
            Student('Steven', 'London', '4', ['foo']),
        ]
        course = Course('foo', 1, 2, 3, 0, 0, 4, enrolled_students)
        groups = course.create_seminar_student_groups()
        self.assertEqual(len(groups), 2)

    def test_create_pracicum_student_groups(self) -> None:
        enrolled_students = [
            Student('John', 'Doe', '1', ['foo']),
            Student('Mary', 'Jane', '2', ['foo']),
            Student('Mike', 'Smith', '3', ['foo']),
            Student('Steven', 'London', '4', ['foo']),
        ]
        course = Course('foo', 1, 0, 0, 2, 3, 4, enrolled_students)
        groups = course.create_practical_student_groups()
        self.assertEqual(len(groups), 2)

    def test_set_conflicting_courses(self) -> None:
        course = Course('foo', 1, 0, 0, 2, 3, 4)
        self.assertEqual(course.conflicting_courses, [])
        course.set_conflicting_courses(['foo', 'bar'])
        self.assertEqual(course.conflicting_courses, ['foo', 'bar'])
