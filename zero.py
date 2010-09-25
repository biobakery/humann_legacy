#!/usr/bin/env python

import sys

for strLine in sys.stdin:
	astrLine = strLine.split( "\t" )
	for i in range( len( astrLine ) ):
		astrLine[i] = astrLine[i].strip( )
		if not astrLine[i]:
			astrLine[i] = "0"
	print( "\t".join( astrLine ) )
