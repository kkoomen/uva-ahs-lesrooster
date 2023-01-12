import csv
from code.entities.course import Course
from code.entities.room import Room
from code.entities.student import Student
from code.utils.helpers import data_path


def load_rooms() -> list[Room]:
    """
    Load the lecture rooms data and create Room instances for each row.
    """
    rooms = []
    with open(data_path('zalen.csv'), 'r') as file:
        # Skip the header.
        file.readline()

        reader = csv.reader(file)
        for row in reader:
            room_id = row[0].strip()
            capacity = int(row[1])
            rooms.append(Room(room_id, capacity))
        file.close()
    return rooms


def load_courses() -> list[Course]:
    """
    Load the courses data and create Student instances for each row.
    """
    courses = []
    with open(data_path('vakken.csv'), 'r') as file:
        # Skip the header.
        file.readline()

        reader = csv.reader(file)
        for row in reader:
            name = row[0].strip()
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
    with open(data_path('studenten_en_vakken.csv'), 'r') as file:
        # Skip the header.
        file.readline()

        reader = csv.reader(file)
        for row in reader:
            last_name, first_name, student_number = row[:3]
            enrolled_courses = [course.strip() for course in row[3:8] if course]
            student = Student(first_name, last_name, student_number, enrolled_courses)
            students.append(student)
        file.close()
    return students
