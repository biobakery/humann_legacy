#!/usr/bin/env python

import sys

if len( sys.argv ) != 2:
	raise Exception( "Usage: trim_fastq.py <len>" )
iLen = int(sys.argv[1])

iLine = -1
for strLine in sys.stdin:
	iLine = ( iLine + 1 ) % 4
	if iLine in (1, 3):
		strLine = strLine[-( iLen + 1 ):]
	sys.stdout.write( strLine )
