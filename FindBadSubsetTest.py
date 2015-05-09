import os
import unittest

from contextlib import contextmanager
from subprocess import check_output
from tempfile import mkstemp
from FindBadSubset import FindBadSubset


@contextmanager
def createUnopenedTemporary():
    try:
        handle, filename = mkstemp()
        yield filename
    finally:
        os.unlink(filename)


class TestFindBadSubset(unittest.TestCase):

    def setUp(self):
        self.seq = list(range(10))

    def test_binary_split(self):
        current_files = set()

        def all_even():
            return all(int(x) % 2 == 0 for x in current_files)

        find_bad_subset = FindBadSubset(
            include_cmd=current_files.update,
            exclude_cmd=current_files.difference_update,
            test_cmd=all_even,
            elements=[str(x) for x in range(10)])

        find_bad_subset.binary_split()

        self.assertEqual(
            find_bad_subset.good_set, set(['0', '2', '4', '6', '8']))
        self.assertEqual(
            find_bad_subset.bad_set, set(['1', '3', '5', '7', '9']))
        self.assertEqual(find_bad_subset.unknown_set, set())

    def test_run_script(self):
        with createUnopenedTemporary() as temp_filename:
            command = ['./FindBadSubset.py',
                       '--include-command', 'testing/add_lines.py', temp_filename,
                       '--exclude-command', 'testing/remove_lines.py', temp_filename,

                       # Success if the file does not contain the letter 'x'.
                       # Note the use of '@' to escape the leading dash.
                       '--test-command', 'testing/not', 'grep', '@-q', 'x', temp_filename,

                       '--elements', 'merry xmas', 'xray', 'an innocuous element', 'hello', 'find x', 'this string is ok'
                       ]

            # Run command, and find the last print out of 'good', 'bad' and
            # 'unknown' sets
            good_set, bad_set, unknown_set = None, None, None
            for line in check_output(command).split('\n'):
                if line.startswith('Good '):
                    good_set = line
                elif line.startswith('Bad '):
                    bad_set = line
                elif line.startswith('Unknown '):
                    unknown_set = line

            self.assertIsNotNone(good_set, 'No good set was reported')
            self.assertIsNotNone(bad_set, 'No bad set was reported')
            self.assertIsNotNone(unknown_set, 'No unknown set was reported')

            good_set = self.parse_set(good_set)
            bad_set = self.parse_set(bad_set)
            unknown_set = self.parse_set(unknown_set)

            self.assertEqual(
                good_set, set(['an innocuous element', 'hello', 'this string is ok']))
            self.assertEqual(bad_set, set(['merry xmas', 'xray', 'find x']))
            self.assertEqual(unknown_set, set())

    # Parse line in the form:
    #     blah blah blah: item1, this is item2, item3
    # Into the set:
    #     set(['item1, 'this is item2', 'item3'])
    def parse_set(self, line):
        _, raw_set = line.split(': ', 1)

        # Special case of empty set
        if raw_set == '':
            return set()

        element_list = raw_set.split(', ')
        element_set = set(element_list)

        self.assertEqual(
            len(element_list), len(element_set), 'Set contains duplicates')
        return element_set


if __name__ == '__main__':
    unittest.main()
