class LectureRoom:
    """
    Lecture rooms are used for hoorcollege, werkcollege and practica lectures
    and can be assigned to an `Event` in order to schedule that `Event` in a
    particular lecture room.
    """

    def __init__(self, room_id: str, capacity: int) -> None:
        self.room_id = room_id
        self.capacity = capacity

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(room_id:{self.room_id}, capacity:{self.capacity})'
