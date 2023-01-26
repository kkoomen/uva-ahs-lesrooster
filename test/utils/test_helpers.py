import os
import random
from unittest import TestCase
import re

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
        self.assertEqual(re.match(r'^\+\d{2}:\d{2}$', get_utc_offset()) is not None, True)

    def test_serialize(self):
        class Bar:
            def serialize(self):
                return {'bar': True}

        class Foo:
            def serialize(self):
                return ['a', Bar()]

        self.assertEqual(serialize(Foo()), ['a', {'bar': True}])
        self.assertEqual(serialize([Foo()]), [['a', {'bar': True}]])
        self.assertEqual(
            serialize({
                'foo': Foo(),
                'foo_list': [Foo(), Foo()],
            }),
            {
                'foo': ['a', {'bar': True}],
                'foo_list': [
                    ['a', {'bar': True}],
                    ['a', {'bar': True}],
                ],
            }
        )
