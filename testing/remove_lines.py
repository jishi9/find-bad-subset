#!/usr/bin/python

##
## Removes each of ARGS from TARGET_FILE (if existent)
##
## ./remove_lines.py TARGET_FILE [ARGS...]

import fileinput
import sys

target_file = sys.argv[1]
lines_to_remove = frozenset(sys.argv[2:])

def strip_newline(line):
	if line[-1] == '\n':
		return line[:-1]
	else:
		return line

# inplace means that we are overwriting the file with whatever we print
for line in fileinput.input(target_file, inplace=True):
	if strip_newline(line) in lines_to_remove:
		continue
	else:
		print line,
