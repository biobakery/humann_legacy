#!/usr/bin/env python

import re
import sys

strKO = None
hashCOGs = {}
for strLine in sys.stdin:
	mtch = re.search( '^ENTRY\s+(K\d+)', strLine )
	if mtch:
		strKO = mtch.group( 1 )
		continue
	mtch = re.search( '^(?:DBLINKS)?\s*COG:(.+)$', strLine )
	if mtch:
		hashCOGs.setdefault( strKO, [] ).extend( mtch.group( 1 ).strip( ).split( " " ) )

for strKO, astrCOGs in hashCOGs.items( ):
	print( "\t".join( [strKO] + astrCOGs ) )
