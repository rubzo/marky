#!/usr/bin/env python

import sys

suite = 0
if (len(sys.argv) > 1):
	suite = __import__(sys.argv[1])
else:
	print "Unable to load a benchmark description file!"
	print "usage: marky.py <benchmark description file>"
	exit(1)

results = suite.run()
if ("--print" in sys.argv):
	suite.print_results(results)
if ("--save" in sys.argv):
	suite.save_results("output.json", results)
