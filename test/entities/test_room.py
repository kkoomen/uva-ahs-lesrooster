from unittest import TestCase

from code.entities.room import Room

class TesttRoom(TestCase):

    def test_init(self):
        r1 = Room('C0.110', 20)
        self.assertEqual(r1.location_id, 'C0.110')
        self.assertEqual(r1.capacity, 20)
        self.assertEqual(r1.is_largest, False)

        r2 = Room('C0.110', 20, True)
        self.assertEqual(r2.location_id, 'C0.110')
        self.assertEqual(r2.capacity, 20)
        self.assertEqual(r2.is_largest, True)

    def test_repr(self):
        r = Room('C0.110', 20)
        self.assertEqual(repr(r), 'Room(location_id:C0.110, capacity:20, is_largest:False)')

    def test_str(self):
        r = Room('C0.110', 20)
        self.assertEqual(str(r), 'C0.110')

    def test_eq(self):
        r1 = Room('C0.110', 10)
        r2 = Room('C0.110', 20)
        r3 = Room('C1.04', 30)
        self.assertEqual(r1 == r2, True)
        self.assertEqual(r1 == r3, False)

    def test_ne(self):
        r1 = Room('C0.110', 10)
        r2 = Room('C0.110', 20)
        r3 = Room('C1.04', 30)
        self.assertEqual(r1 != r2, False)
        self.assertEqual(r1 != r3, True)

    def test_lt(self):
        r1 = Room('C0.110', 10)
        r2 = Room('C0.110', 20)
        self.assertEqual(r1 < r2, True)
        self.assertEqual(r2 < r1, False)

    def test_sorting(self):
        r1 = Room('C0.110', 20)
        r2 = Room('C1.04', 10)
        r3 = Room('C1.08', 15)
        self.assertEqual(sorted([r1, r2, r3]) == [r2, r3, r1], True)

    def test_set_is_largest(self):
        r = Room('C0.110', 20)
        self.assertEqual(r.is_largest, False)
        r.set_is_largest(True)
        self.assertEqual(r.is_largest, True)
