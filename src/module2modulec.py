#!/usr/bin/env python

import re
import sys

astrEntry = fDefinition = None
for strLine in sys.stdin:
	if not fDefinition:
		mtch = re.search( '^ENTRY\s+(M\d+)', strLine )
		if mtch:
			astrEntry = [mtch.group( 1 )]
			continue
		mtch = re.search( '^NAME\s+(.+)$', strLine )
		if mtch:
#			astrEntry[0] += ":" + mtch.group( 1 ).replace( " ", "_" )
			continue
		if strLine.find( "DEFINITION" ) == 0:
			fDefinition = True
	if fDefinition:
		mtch = re.search( '^(?:DEFINITION)?\s+(.+)$', strLine )
		if not mtch:
			print( "\t".join( astrEntry ) )
			fDefinition = False
			continue
		for strToken in mtch.group( 1 ).split( " " ):
			astrEntry += filter( lambda s: s, re.split( '[,+]', re.sub( '[\-()]', "", strToken ) ) )
