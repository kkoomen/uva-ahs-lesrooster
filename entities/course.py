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
                 enrolment: int) -> None:
        self.name = name
        self.lectures_amount = lectures_amount
        self.seminars_amount = seminars_amount
        self.seminar_capacity = seminar_capacity
        self.practicals_amount = practicals_amount
        self.practical_capacity = practical_capacity
        self.enrolment = enrolment

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(name:{self.name}, lectures_amount:{self.lectures_amount}, seminars_amount:{self.seminars_amount}, seminar_capacity:{self.seminar_capacity}, practicals_amount:{self.practicals_amount}, practical_capacity:{self.practical_capacity}, enrolment:{self.enrolment})'
