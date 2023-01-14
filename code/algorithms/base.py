import abc

from code.entities.timetable import Timetable


class Algorithm(abc.ABC):
    timetable: Timetable

    @abc.abstractmethod
    def run(self) -> tuple[bool, int]:
        """
        Run the algorithm until a solution is found.

        :returns: tuple containing the following info respectively:
          - bool: whether a solution has been found or not
          - int: the total amount of retries
        """
        pass
