from unittest import TestCase

from code.entities.student import Student

class TestStudent(TestCase):

    def test_init(self):
        student = Student('John', 'Doe', '12345678', ['course1', 'course2'])
        self.assertEqual(student.first_name, 'John')
        self.assertEqual(student.last_name, 'Doe')
        self.assertEqual(student.student_id, '12345678')
        self.assertEqual(student.enrolled_courses, ['course1', 'course2'])

    def test_repr(self):
        student = Student('John', 'Doe', '12345678', ['course1', 'course2'])
        self.assertEqual(repr(student), "Student(first_name:John, last_name:Doe, student_id:12345678, enrolled_courses:['course1', 'course2'])")

    def test_str(self):
        student = Student('John', 'Doe', '12345678', ['course1', 'course2'])
        self.assertEqual(str(student), 'John Doe')

    def test_get_full_name(self):
        student = Student('John', 'Doe', '12345678', ['course1', 'course2'])
        self.assertEqual(student.get_full_name(), 'John Doe')
