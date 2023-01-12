class Student:
    """
    Students contain personal information such as their name and student number,
    but also contain the courses they have enrolled in.
    """

    def __init__(self,
                 first_name: str,
                 last_name: str,
                 student_number: str,
                 enrolled_courses: list[str]) -> None:
        self.first_name = first_name
        self.last_name = last_name
        self.student_number = student_number
        self.enrolled_courses = enrolled_courses

    def __repr__(self):
        return f'{self.__class__.__name__}(first_name:{self.first_name}, last_name:{self.last_name}, student_number:{self.student_number}, enrolled_courses:{self.enrolled_courses})'

    def get_full_name(self) -> str:
        return f'{self.first_name} {self.last_name}'
