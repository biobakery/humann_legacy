#!/usr/bin/env python

import re
import sys

fPathways = False
if len( sys.argv ) > 1:
	if sys.argv[1] == "-h":
		raise Exception( "Usage: module2modulec.py [pathways] < <module>" )
	fPathways = int(sys.argv[1]) != 0

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
			if fPathways:
				strToken = strToken.replace( ",", "|" )
			astrEntry += filter( lambda s: s, re.split( '[,+]', re.sub( '[\-()]', "", strToken ) ) )
