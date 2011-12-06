#!/usr/bin/env python

import pathway
import re
import sys

c_iSize	= 4

astrPaths = sys.argv[1:]

hashPaths = {}
for strPaths in astrPaths:
	for pPathway in pathway.open( open( strPaths ) ):
		hashPaths[pPathway.id( )] = min( pPathway.size( ), hashPaths.get( pPathway.id( ), pPathway.size( ) ) )

fFirst = True
for strLine in sys.stdin:
	mtch = re.search( '^([^\t]*)\t', strLine )
	if ( not fFirst ) and mtch:
		iSize = hashPaths.get( mtch.group( 1 ), c_iSize )
		if iSize < c_iSize:
			continue
	fFirst = False
	sys.stdout.write( strLine )
