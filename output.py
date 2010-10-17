#!/usr/bin/env python

import sys

if len( sys.argv ) != 2:
	raise Exception( "Usage: output.py <file>" )
strOut = sys.argv[1]

strLine = sys.stdin.readline( )
if not strLine:
	sys.exit( 1 )
with open( strOut, "w" ) as fileOut:
	fileOut.write( strLine )
	for strLine in sys.stdin:
		fileOut.write( strLine )
