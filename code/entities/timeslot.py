from code.entities.event import Event


class Timeslot:
    """
    Timeslots are used inside the Timetable class and contain scheduled events.
    """

    OPTIONS = [9, 11, 13, 15, 17]

    def __init__(self) -> None:
        self.events = []

    def add_event(self, event: Event) -> None:
        """
        Add an event to the events list.
        """
        self.events.append(event)

    def remove_event(self, event) -> None:
        """
        Remove an event from the events list.
        """
        self.events.remove(event)

    def get_total_events(self) -> int:
        """
        Get the total amount of events.
        """
        return len(self.events)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(events:{len(self.events)})'

    def __iter__(self):
        """
        Allows to iterate over the timeslot events.
        """
        for event in self.events:
            yield event

    def get_duplicate_course_events(self) -> list[Event]:
        """
        Find duplicate events for a specific course in a certain timeslot.
        """
        duplicated_events = []
        visited_courses = []

        for event in self.events:
            if event.course in visited_courses:
                duplicated_events.append(event)
            else:
               visited_courses.append(event.course)

        return duplicated_events

    def get_double_booked_events(self) -> list[Event]:
        """
        Find the events that are booked in the same room.
        """
        double_booked_events = []
        visited_room_ids = []

        for event in self.events:
            if event.room.location_id in visited_room_ids:
                double_booked_events.append(event)
            else:
                visited_room_ids.append(event.room.location_id)

        return double_booked_events
