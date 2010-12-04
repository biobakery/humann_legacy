#!/usr/bin/env python

import re
import sys

c_iSize	= 4

astrPaths = sys.argv[1:]

hashPaths = {}
for strPaths in astrPaths:
	for strLine in open( strPaths ):
		astrLine = strLine.strip( ).split( "\t" )
		hashPaths[astrLine[0]] = len( astrLine ) - 1

fFirst = True
for strLine in sys.stdin:
	mtch = re.search( '^([^\t]*)\t', strLine )
	if ( not fFirst ) and mtch:
		iSize = hashPaths.get( mtch.group( 1 ), 0 )
		if iSize < c_iSize:
			continue
	fFirst = False
	sys.stdout.write( strLine )
