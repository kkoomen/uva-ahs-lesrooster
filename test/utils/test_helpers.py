import os
import random
from unittest import TestCase

from code.utils.helpers import (
    data_path,
    get_utc_offset,
    remove_duplicates,
    serialize,
    split_list,
    split_list_random,
)

class TestUtilsHelpers(TestCase):

    def test_data_path(self):
        root_dir = os.path.realpath(os.path.join(os.path.basename(__file__), '../'))
        filepath = data_path('foo.csv')
        self.assertEqual(filepath, os.path.join(root_dir, 'data', 'foo.csv'))

    def test_split_list(self):
        self.assertEqual(split_list(['a', 'b', 'c', 'd', 'e'], 2), [['a', 'b'], ['c', 'd'], ['e']])

    def test_split_list_random(self):
        random.seed(0)
        self.assertEqual(split_list_random(['a', 'b', 'c', 'd', 'e'], 2), [['b', 'c'], ['a', 'e'], ['d']])

    def test_make_id(self):
        value = random.getrandbits(32)
        self.assertEqual(isinstance(value, int), True)
        self.assertEqual(len(str(value)) > 0, True)

    def test_remove_duplicates(self):
        self.assertEqual(remove_duplicates(['a', 'b', 'b', 'c']), ['a', 'b', 'c'])

    def test_get_utc_offset(self):
        os.environ['TZ'] = 'Europe/Amsterdam'
        self.assertEqual(get_utc_offset(), '+01:00')

    def test_serialize(self):
        class Foo:
            items = ['a', 'b']
            def serialize(self):
                return self.items

        self.assertEqual(serialize(Foo()), ['a', 'b'])
        self.assertEqual(serialize([Foo()]), [['a', 'b']])
        self.assertEqual(serialize({'foo': Foo(), 'foo_list': [Foo(), Foo()]}), {'foo': ['a', 'b'], 'foo_list': [['a', 'b'], ['a', 'b']]})
