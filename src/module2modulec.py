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
	if fDefinition:
		mtch = re.search( r'^(?:DEFINITION)?\s+(.+)$', strLine )
		if not mtch:
			i = 2
			while i < len( astrEntry ):
				if re.search( r'\W$', astrEntry[i - 1] ):
					astrEntry[i - 1] += astrEntry[i]
					del astrEntry[i]
				else:
					i += 1
			print( "\t".join( filter( lambda s: s, astrEntry ) ) )
			fDefinition = False
			continue
		for strToken in mtch.group( 1 ).split( " " ):
			strToken = re.sub( r'[()]', "", strToken.strip( ) )
			if strToken == "--":
				continue
			if fPathways:
				astrEntry.append( strToken.replace( ",", "|" ).replace( "-", "+~" ) )
			else:
				astrEntry += filter( lambda s: s, re.split( r'[,+-]', strToken ) )
