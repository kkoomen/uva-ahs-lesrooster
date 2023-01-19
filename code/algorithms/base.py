import abc
from typing import Any

from code.entities.timetable import Timetable


class Algorithm(abc.ABC):
    timetable: Timetable
    statistics: list[Any]

    @abc.abstractmethod
    def plot_statistics(self) -> None:
        """
        Plot statistics that were gathered when the algorithm ran.
        """
        pass

    @abc.abstractmethod
    def run(self, iterations: int) -> None:
        """
        Run the algorithm for n-iteraations until a valid solution is found.
        """
        pass
