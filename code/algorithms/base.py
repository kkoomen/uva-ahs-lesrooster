import abc
from typing import Any

from code.entities.timetable import Timetable


class Algorithm(abc.ABC):
    timetable: Timetable

    @abc.abstractmethod
    def run(self) -> Any:
        """
        Run the algorithm until a valid solution is found.
        """
        pass
