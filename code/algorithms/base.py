import abc
from typing import Any

from code.entities.timetable import Timetable


class Algorithm(abc.ABC):
    timetable: Timetable

    @abc.abstractmethod
    def print_average_statistics(self, iterations: int) -> None:
        """
        Run for `iterations` amount of times and print average statistics.
        """
        pass

    @abc.abstractmethod
    def run(self) -> Any:
        """
        Run the algorithm until a valid solution is found.
        """
        pass
