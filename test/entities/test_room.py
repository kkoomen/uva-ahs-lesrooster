from unittest import TestCase

from code.entities.room import Room

class TestRoom(TestCase):

    def test_init(self):
        room1 = Room('C0.110', 20)
        self.assertEqual(room1.location_id, 'C0.110')
        self.assertEqual(room1.capacity, 20)
        self.assertEqual(room1.is_largest, False)

        room2 = Room('C0.110', 20, True)
        self.assertEqual(room2.location_id, 'C0.110')
        self.assertEqual(room2.capacity, 20)
        self.assertEqual(room2.is_largest, True)

    def test_repr(self):
        room = Room('C0.110', 20)
        self.assertEqual(repr(room), 'Room(location_id:C0.110, capacity:20, is_largest:False)')

    def test_str(self):
        room = Room('C0.110', 20)
        self.assertEqual(str(room), 'C0.110')

    def test_eq(self):
        room1 = Room('C0.110', 10)
        room2 = Room('C0.110', 20)
        room3 = Room('C1.04', 30)
        self.assertEqual(room1 == room2, True)
        self.assertEqual(room1 == room3, False)

    def test_ne(self):
        room1 = Room('C0.110', 10)
        room2 = Room('C0.110', 20)
        room3 = Room('C1.04', 30)
        self.assertEqual(room1 != room2, False)
        self.assertEqual(room1 != room3, True)

    def test_lt(self):
        room1 = Room('C0.110', 10)
        room2 = Room('C0.110', 20)
        self.assertEqual(room1 < room2, True)
        self.assertEqual(room2 < room1, False)

    def test_sorting(self):
        room1 = Room('C0.110', 20)
        room2 = Room('C1.04', 10)
        room3 = Room('C1.08', 15)
        self.assertEqual(sorted([room1, room2, room3]) == [room2, room3, room1], True)

    def test_set_is_largest(self):
        room = Room('C0.110', 20)
        self.assertEqual(room.is_largest, False)
        room.set_is_largest(True)
        self.assertEqual(room.is_largest, True)
