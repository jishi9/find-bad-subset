import unittest
from FindBadSubset import FindBadSubset


class FileTracker(object):
    def __init__(self):
        super(FileTracker, self).__init__()
        self.arg = arg


class TestFindBadSubset(unittest.TestCase):

    def setUp(self):
        self.seq = list(range(10))

    def test_binary_split(self):

        current_files = set()

        def all_even():
            return all(int(x) % 2 == 0 for x in current_files)


        find_bad_subset = FindBadSubset(
            include_cmd = current_files.update,
            exclude_cmd = current_files.difference_update,
            test_cmd = all_even,
            elements = [ str(x) for x in range(10) ])

        find_bad_subset.binary_split()

        self.assertEqual(find_bad_subset.good_set, set(['0', '2', '4', '6', '8']))
        self.assertEqual(find_bad_subset.bad_set, set(['1', '3', '5', '7', '9']))
        self.assertEqual(find_bad_subset.unknown_set, set())

if __name__ == '__main__':
    unittest.main()
