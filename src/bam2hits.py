#!/usr/bin/env python

import hits
import sys
import math

pHits = hits.CHits( )
for strLine in sys.stdin:
	astrLine = strLine.rstrip( ).split( "\t" )
	try:
		strTo, strFrom, strE = ( astrLine[2], astrLine[0], astrLine[4] )
	except IndexError:
		sys.stderr.write( "%s\n" % astrLine )
		continue
	try:
		dE = math.pow( 10.0, ( float( strE ) )/( -10.0 ) ) # Local vs. Global
	except ValueError:
		continue
	pHits.add( strTo, strFrom, dE, 1, 1 )
pHits.save( sys.stdout )
