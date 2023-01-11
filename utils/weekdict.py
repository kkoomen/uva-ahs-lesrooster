from entities.event import Event


class WeekDict(dict):
    """
    Custom dictionary type that is used for the Timetable class and its events.
    The key must be a day of the week.
    The value must a list of `Event` classes.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __setitem__(self, key, value):
        if key not in ['mon', 'tue', 'wed', 'thu', 'fri']:
            raise KeyError("Invalid key: must be one of 'mon', 'tue', 'wed', 'thu', or 'fri'")
        if not all(isinstance(i, Event) for i in value):
            raise TypeError("Invalid value: must be a list of Event classes")
        super().__setitem__(key, value)
