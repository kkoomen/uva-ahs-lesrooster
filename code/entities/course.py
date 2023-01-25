import math
from typing import Union

from code.entities.student import Student
from code.utils.enums import EventType
from code.utils.helpers import make_id, split_list, split_list_random


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
        self.conflicting_courses: list[str] = []

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(id:{self.id}, name:{self.name}, enrolled_students:{len(self.enrolled_students)})'

    def __eq__(self, other) -> bool:
        """
        Check if two courses are of the same class type and have the same id.
        """
        return self.__class__ == other.__class__ and self.id == other.id

    def get_capacity_for_type(self, event_type: EventType) -> int:
        """
        Get the capacity for a specific type.
        """
        if event_type == EventType.SEMINAR:
            return self.seminar_capacity

        if event_type == EventType.PRACTICUM:
            return self.practical_capacity

        return self.enrolment

    def register_students(self, students: list[Student]) -> None:
        """
        Register a list of students to this course.
        """
        self.enrolled_students = students

    def calculate_total_events(self) -> int:
        """
        Calculate how many events this course will schedule based on lectures,
        seminars and practicals amount and capacity along with the enrolment.
        """
        total = self.lectures_amount

        if self.seminars_amount > 0:
            total += math.ceil(self.enrolment / self.seminar_capacity * self.seminars_amount)

        if self.practicals_amount > 0:
            total += math.ceil(self.enrolment / self.practical_capacity * self.practicals_amount)

        return total

    def create_student_groups(self, capacity: int, random=False) -> tuple[list[list[Student]], int]:
        """
        Create student groups based on a certain capacity.

        :returns: List with grouped students and total groups created.
        """
        total_groups = math.ceil(self.enrolment / capacity)
        group_capacity = math.ceil(self.enrolment / total_groups)
        fn = split_list_random if random else split_list
        return fn(self.enrolled_students, group_capacity), total_groups

    def create_seminar_student_groups(self, random=False) -> tuple[list[list[Student]], int]:
        """
        Create student groups based on the seminar capacity.
        """
        return self.create_student_groups(self.seminar_capacity, random)

    def create_practical_student_groups(self, random=False) -> tuple[list[list[Student]], int]:
        """
        Create student groups based on the practical capacity.
        """
        return self.create_student_groups(self.practical_capacity, random)

    def set_conflicting_courses(self, courses: list[str]) -> None:
        """
        Set the conflicting courses value.
        """
        self.conflicting_courses = courses
