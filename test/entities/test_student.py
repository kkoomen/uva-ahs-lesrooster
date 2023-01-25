#!/usr/bin/env python3


from unittest import TestCase

from code.entities.student import Student

class TestStudent(TestCase):

    def test_property_values(self):
        first_name = 'John'
        last_name = 'Doe'
        student_id = '12345678'
        enrolled_courses = ['course1', 'course2']
        s = Student(first_name, last_name, student_id, enrolled_courses)
        self.assertEqual(s.first_name, first_name)
        self.assertEqual(s.last_name, last_name)
        self.assertEqual(s.student_id, student_id)
        self.assertEqual(s.enrolled_courses, enrolled_courses)
