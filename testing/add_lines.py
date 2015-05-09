#!/usr/bin/python

##
## Append each of ARGS to TARGET_FILE
##
## ./add_lines.py TARGET_FILE [ARGS...]

import sys

target_file = sys.argv[1]
lines_to_add = sys.argv[2:]

with open(target_file, 'a') as f:
	for line in lines_to_add:
		print >> f, line
