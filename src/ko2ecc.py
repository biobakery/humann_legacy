#!/usr/bin/env python

import re
import sys

fDefinition = astrECs = None
hashECs = {}
for strLine in sys.stdin:
	mtch = re.search( '^ENTRY\s+(K\d+)', strLine )
	if mtch:
		hashECs[mtch.group( 1 )] = astrECs = []
	elif strLine.startswith( "DEFINITION" ):
		fDefinition = True
	if fDefinition:
		mtch = re.search( '^(?:(?:DEF)|\s)', strLine )
		if not mtch:
			fDefinition = False
		else:
			while True:
				mtch = re.search( '(\d+\.\d+\.\d+\.\d+)(.*)', strLine )
				if not mtch:
					break
				astrECs.append( mtch.group( 1 ) )
				strLine = mtch.group( 2 )

for strKO, astrECs in hashECs.items( ):
	if astrECs:
		print( "\t".join( [strKO] + astrECs ) )
