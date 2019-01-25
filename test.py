#!/usr/bin/env python3

from collections import OrderedDict
from po          import Reader, Writer
from sys         import stdin, stdout

w = Writer(stdout)
for e in Reader(OrderedDict, stdin):
	print(e)
	w.write(e)
