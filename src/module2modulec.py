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
		mtch = re.search( r'^ENTRY\s+(M\d+)', strLine )
		if mtch:
			astrEntry = [mtch.group( 1 )]
			continue
		mtch = re.search( r'^NAME\s+(.+)$', strLine )
		if mtch:
#			astrEntry[0] += ":" + mtch.group( 1 ).replace( " ", "_" )
			continue
		if strLine.find( "DEFINITION" ) == 0:
			fDefinition = True
	if astrEntry and fDefinition:
		mtch = re.search( r'^(?:DEFINITION)?\s+(.+)$', strLine )
		if not mtch:
			if fPathways:
				i = 0
				while ( i + 1 ) < len( astrEntry ):
					if astrEntry[i] and ( "(,|+-".find( astrEntry[i][-1] ) >= 0 ):
						astrEntry[i] += astrEntry[i + 1]
						del astrEntry[i + 1]
						i -= 1
					i += 1
			else:
				astrEntry = [astrEntry[0]] + list(set(astrEntry[1:]))
			print( "\t".join( filter( lambda s: s, astrEntry ) ) )
			fDefinition = astrEntry = None
			continue
		for strToken in re.split( r'\s+', mtch.group( 1 ) ):
			strToken = strToken.strip( )
			if strToken == "--":
				continue
			if fPathways:
				astrEntry.append( strToken )
			else:
				astrEntry += filter( lambda s: s, re.split( r'[,+-]', re.sub( r'[()]', "", strToken ) ) )
