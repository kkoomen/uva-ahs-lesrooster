#!/usr/bin/env python3

import csv

from entities.course import Course
from entities.lecture_room import LectureRoom
from entities.student import Student
from utils.helpers import asset_path


def load_lecture_rooms() -> list[LectureRoom]:
    """
    Load the lecture rooms data and create LectureRoom instances for each row.
    """
    lecture_rooms = []
    with open(asset_path('zalen.csv'), 'r') as file:
        # Skip the header.
        file.readline()

        reader = csv.reader(file)
        for row in reader:
            room_id, capacity = row
            lecture_rooms.append(LectureRoom(room_id, int(capacity)))
        file.close()
    return lecture_rooms


def load_courses() -> list[Course]:
    """
    Load the courses data and create Student instances for each row.
    """
    courses = []
    with open(asset_path('vakken.csv'), 'r') as file:
        # Skip the header.
        file.readline()

        reader = csv.reader(file)
        for row in reader:
            name = row[0]
            lectures_amount = int(row[1])
            seminars_amount = int(row[2])
            seminar_capacity = int(row[3] or 0)
            practicals_amount = int(row[4])
            practical_capacity = int(row[5] or 0)
            enrolment = int(row[6])

            course = Course(
                name,
                lectures_amount,
                seminars_amount,
                seminar_capacity,
                practicals_amount,
                practical_capacity,
                enrolment,
            )

            courses.append(course)
        file.close()
    return courses


def load_students() -> list[Student]:
    """
    Load the students data and create Student instances for each row.
    """
    students = []
    with open(asset_path('studenten_en_vakken.csv'), 'r') as file:
        # Skip the header.
        file.readline()

        reader = csv.reader(file)
        for row in reader:
            last_name, first_name, student_number = row[:3]
            enrolled_courses = [course for course in row[3:8] if course]
            student = Student(first_name, last_name, student_number, enrolled_courses)
            students.append(student)
        file.close()
    return students


def main():
    lecture_rooms = load_lecture_rooms()
    courses = load_courses()
    students = load_students()

    # TODO: output them in the expected format


if __name__ == '__main__':
    main()
