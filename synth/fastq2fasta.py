#!/usr/bin/env python

import sys

iLine = 0
for strLine in sys.stdin:
	iCur = iLine % 4
	iLine += 1
	if iCur == 0:
		strLine = strLine.replace( "@gn:", "> " )
	elif iCur > 1:
		continue
	sys.stdout.write( strLine )
