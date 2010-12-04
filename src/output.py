#!/usr/bin/env python

import sys

if len( sys.argv ) != 2:
	raise Exception( "Usage: output.py <file>" )
strOut = sys.argv[1]

strLine = sys.stdin.readline( )
if not strLine:
	sys.exit( 1 )
fileOut = open( strOut, "w" )
fileOut.write( strLine )
for strLine in sys.stdin:
	fileOut.write( strLine )
fileOut.close( )
