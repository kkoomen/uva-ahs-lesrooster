import os
import random
from unittest import TestCase
import re
from code.utils.constants import ROOT_DIR

from code.utils.helpers import (
    data_path,
    get_utc_offset,
    remove_duplicates,
    serialize,
    split_list,
    split_list_random,
)

class TestUtilsHelpers(TestCase):

    def test_data_path(self) -> None:
        filepath = data_path('foo.csv')
        self.assertEqual(filepath, os.path.join(ROOT_DIR, 'data', 'foo.csv'))

    def test_split_list(self) -> None:
        self.assertEqual(split_list(['a', 'b', 'c', 'd', 'e'], 2), [['a', 'b'], ['c', 'd'], ['e']])
        self.assertEqual(split_list(['a', 'b', 'c', 'd', 'e'], 4), [['a', 'b', 'c', 'd'], ['e']])

    def test_split_list_random(self) -> None:
        random.seed(0)
        self.assertEqual(split_list_random(['a', 'b', 'c', 'd', 'e'], 2), [['d', 'e'], ['a', 'c'], ['b']])
        self.assertEqual(split_list_random(['a', 'b', 'c', 'd', 'e'], 4), [['d', 'c', 'b', 'e'], ['a']])

    def test_make_id(self) -> None:
        value = random.getrandbits(32)
        self.assertEqual(isinstance(value, int), True)
        self.assertEqual(len(str(value)) > 0, True)

    def test_remove_duplicates(self) -> None:
        self.assertEqual(remove_duplicates(['a', 'b', 'b', 'c']), ['a', 'b', 'c'])

    def test_get_utc_offset(self) -> None:
        self.assertEqual(re.match(r'^\+\d{2}:\d{2}$', get_utc_offset()) is not None, True)

    def test_serialize(self) -> None:
        class Bar:
            def serialize(self) -> dict[str, bool]:
                return {'bar': True}

        class Foo:
            def serialize(self) -> list:
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
