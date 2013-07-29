#!/usr/bin/env python

import sys
import logging

logging.basicConfig(filename='1example.log',level=logging.DEBUG)

iLen = None if ( len( sys.argv ) <= 1 ) else sys.argv[1]

astrLines = []
for strLine in sys.stdin:
	if not astrLines:
		strLine = strLine.replace( "@gn:", ">" )
	elif len( astrLines ) >= 3:
		astrLines = []
		continue
	astrLines.append( strLine.strip( ) )
	logging.debug( astrLines )
	if ( len( astrLines ) == 2 ) and ( ( not iLen ) or ( len( strLine ) >= iLen ) ):
		print( "\n".join( astrLines ) )
