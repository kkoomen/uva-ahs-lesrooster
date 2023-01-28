from unittest import TestCase

from code.entities.student import Student

class TestStudent(TestCase):

    def test_init(self) -> None:
        student = Student('John', 'Doe', '1', ['course1', 'course2'])
        self.assertEqual(student.first_name, 'John')
        self.assertEqual(student.last_name, 'Doe')
        self.assertEqual(student.student_id, '1')
        self.assertEqual(student.enrolled_courses, ['course1', 'course2'])

    def test_str(self) -> None:
        student = Student('John', 'Doe', '1', ['course1', 'course2'])
        self.assertEqual(str(student), 'John Doe')

    def test_get_full_name(self) -> None:
        student = Student('John', 'Doe', '1', ['course1', 'course2'])
        self.assertEqual(student.get_full_name(), 'John Doe')

    def test_eq(self) -> None:
        student1 = Student('John', 'Doe', '1', ['course 1', 'course 2'])
        student2 = Student('John', 'Doe', '1', ['course 1', 'course 2'])
        student3 = Student('Mary', 'Jane', '2', ['course 1'])
        self.assertEqual(student1 == student1, True)
        self.assertEqual(student1 == student2, True)
        self.assertEqual(student1 == student3, False)
