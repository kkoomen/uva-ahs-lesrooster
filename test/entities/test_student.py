from unittest import TestCase

from code.entities.student import Student

class TestStudent(TestCase):

    def test_init(self):
        s = Student('John', 'Doe', '12345678', ['course1', 'course2'])
        self.assertEqual(s.first_name, 'John')
        self.assertEqual(s.last_name, 'Doe')
        self.assertEqual(s.student_id, '12345678')
        self.assertEqual(s.enrolled_courses, ['course1', 'course2'])

    def test_repr(self):
        s = Student('John', 'Doe', '12345678', ['course1', 'course2'])
        self.assertEqual(repr(s), "Student(first_name:John, last_name:Doe, student_id:12345678, enrolled_courses:['course1', 'course2'])")

    def test_str(self):
        s = Student('John', 'Doe', '12345678', ['course1', 'course2'])
        self.assertEqual(str(s), 'John Doe')

    def test_get_full_name(self):
        s = Student('John', 'Doe', '12345678', ['course1', 'course2'])
        self.assertEqual(s.get_full_name(), 'John Doe')
