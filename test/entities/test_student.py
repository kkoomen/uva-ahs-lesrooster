from unittest import TestCase

from code.entities.student import Student

class TestStudent(TestCase):

    def test_init(self):
        student = Student('John', 'Doe', '1', ['course1', 'course2'])
        self.assertEqual(student.first_name, 'John')
        self.assertEqual(student.last_name, 'Doe')
        self.assertEqual(student.student_id, '1')
        self.assertEqual(student.enrolled_courses, ['course1', 'course2'])

    def test_str(self):
        student = Student('John', 'Doe', '1', ['course1', 'course2'])
        self.assertEqual(str(student), 'John Doe')

    def test_get_full_name(self):
        student = Student('John', 'Doe', '1', ['course1', 'course2'])
        self.assertEqual(student.get_full_name(), 'John Doe')
