#!/usr/bin/python

from itertools import islice
from Queue import PriorityQueue
from subprocess import call, check_call
import sys
import argparse


def take(n, iterable):
    return list(islice(iterable, n))


def take_half(items):
    num_items = len(items)
    itr = iter(items)
    half_1 = set(take(num_items / 2, itr))
    half_2 = set(itr)
    return half_1, half_2


class FindBadSubset(object):

    def __init__(self, include_cmd, exclude_cmd, test_cmd, elements):
        self.include_cmd = include_cmd
        self.exclude_cmd = exclude_cmd
        self.test_cmd = test_cmd
        self.elements = frozenset(elements)

        # Initially all elements are unknown
        self.unknown_set = set(self.elements)
        self.good_set = set()
        self.bad_set = set()

    def is_good(self, include_set):
        exclude_set = self.elements - include_set

        self.include_cmd(include_set)
        self.exclude_cmd(exclude_set)

        return self.test_cmd()

    def _display_set(self, name, set_to_print):
        return '%s (%d): %s' % (
            name, len(set_to_print), ', '.join(set_to_print))

    def print_status(self):
        print self._display_set('Good', self.good_set)
        print self._display_set('Bad', self.bad_set)
        print self._display_set('Unknown', self.unknown_set)
        print

    def binary_split(self):
        # Queue prioritizes larger jobs.
        q = PriorityQueue()

        def put_job(elems):
            if elems:
                q.put((len(elems), elems))

        def pop_job():
            size, elems = q.get_nowait()
            return elems

        put_job(set(self.unknown_set))

        while not q.empty():
            # Remove any known-good or known-bad elements.
            unknowns = pop_job() - self.good_set - self.bad_set

            # If the effective set of unknowns is empty, move on to the next
            # job.
            if not unknowns:
                continue

            # Elements to test
            print '%d unknown elements currently under test' % len(unknowns)
            include_set = unknowns | self.good_set

            # All included elments are good. Move them all from unknown_set to
            # good_set.
            if self.is_good(include_set):
                self.unknown_set -= include_set
                self.good_set |= include_set

            # Some of the included elements are bad
            else:
                # Only one unknown element, this is the culprit. Move it form
                # unknown_set to bad_set.
                if len(unknowns) == 1:
                    assert not (unknowns & self.bad_set)
                    self.unknown_set -= unknowns
                    self.bad_set |= unknowns
                # Can't tell which of the unknown elements are bad, split into
                # two groups and enqueu.
                else:
                    unknowns_1, unknowns_2 = take_half(unknowns)
                    put_job(unknowns_1)
                    put_job(unknowns_2)

            self.print_status()


def to_shell_callable(cmds):
    def fun():
        try:
            return call(cmds) == 0
        except OSError:
            print >> sys.stderr, 'Could not execure command:', cmds
            raise

    return fun


def to_nofail_shell_callable_with_args(cmds):
    def fun(args):
        try:
            command = cmds + list(args)
            check_call(command)
        except CalledProcessError:
            print >> sys.stderr, 'Command failed:', command
            raise

    return fun


parser = argparse.ArgumentParser(
    description='Detect the subset of bad elements through bisection-based search.',
    epilog="Escape any arguments that start with a '-' with '@', so that 'grep -q x' becomes 'grep @-q x'.")

parser.add_argument(
    '--include-command',
    '-i',
    nargs='+',
    required=True,
    help='Command to include a number of elements in the next test. This should accept a variable number of elements as arguments.')
parser.add_argument(
    '--exclude-command',
    '-x',
    nargs='+',
    required=True,
    help='Command to exclude a number of elements in the next test. This should accept a variable number of elements as arguments.')
parser.add_argument(
    '--test-command',
    '-t',
    nargs='+',
    required=True,
    help='Command run to test whether the currently included set of elements. This should exit with zero status if all elements are "good", ' +
    'otherwise it should exit with a non-zero status.')
parser.add_argument('--elements', '-e', nargs='+', required=True,
                    help='The set of elements.')


def unescape_dash_argument(arg):
    if arg.startswith('@'):
        return arg[1:]
    else:
        return arg


def main(include_cmd, exclude_cmd, test_cmd, elements):
    finder = FindBadSubset(include_cmd, exclude_cmd, test_cmd, elements)
    finder.print_status()
    finder.binary_split()
    finder.print_status()


if __name__ == '__main__':
    args = parser.parse_args()
    include_command = map(unescape_dash_argument, args.include_command)
    exclude_command = map(unescape_dash_argument, args.exclude_command)
    test_command = map(unescape_dash_argument, args.test_command)

    main(to_nofail_shell_callable_with_args(include_command),
         to_nofail_shell_callable_with_args(exclude_command),
         to_shell_callable(test_command),
         args.elements)
