from typing import Union
from code.entities.student import Student
from code.utils.helpers import make_id


class Course:
    """
    Courses contain information about the amount of lectures, seminars and
    practicals that will be held, the capacity for seminars and practicals and
    the amount of enrolments.
    """

    def __init__(self,
                 name: str,
                 lectures_amount: int,
                 seminars_amount: int,
                 seminar_capacity: int,
                 practicals_amount: int,
                 practical_capacity: int,
                 enrolment: int,
                 enrolled_students: Union[None, list[Student]]=None) -> None:
        self.id = make_id()
        self.name = name
        self.lectures_amount = lectures_amount
        self.seminars_amount = seminars_amount
        self.seminar_capacity = seminar_capacity
        self.practicals_amount = practicals_amount
        self.practical_capacity = practical_capacity
        self.enrolment = enrolment
        self.enrolled_students = enrolled_students if enrolled_students is not None else []

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(name:{self.name}, enrolled_students:{len(self.enrolled_students)})'

    def register_students(self, students: list[Student]) -> None:
        """
        Register a list of students to this course.
        """
        self.enrolled_students = students
