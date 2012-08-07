#!/usr/bin/env python

import hits
import sys
import re

if len( sys.argv ) < 2:
	raise Exception( "Usage: pathways2lefse.py <ko> < <input.txt>" )
strKOc = sys.argv[1]

iLine = 18
iCLine = 0

setPaths = set()
hashOrgs = {}
fOrg = False
for strLine in sys.stdin:
	astrLine = strLine.rstrip( ).split( "\t" )
	if iCLine == iLine:
		if fOrg:
			setPaths.add( ( astrLine[0], astrLine[2] ) )
		else:
			setPaths.add( astrLine[0] )
	elif astrLine[0] == "ID":
		fOrg = astrLine[2] == "Organism"
	else:
		iCLine += 1

hashMeta = {}
pattern = re.compile('[\W_]+')
fClass = False
for strLine in open( strKOc ):
	if strLine[0] != ' ':
		fClass = strLine.find( "CLASS" ) >= 0
	if fClass:
		strLine = strLine[12:]
		if strLine.find( " [PATH:" ) >= 0:
			strLine, strKO = strLine.split( " [PATH:" )
			strKO = pattern.sub( "", strKO )
			astrLine = strLine.split( "; " )
			for i in range( len( astrLine ) ):
				astrLine[i] = pattern.sub( "_", astrLine[i] )
			hashMeta[strKO] = astrLine

if fOrg:
	for ( strKO, strOrg ) in setPaths:
		print( "|".join( hashMeta.setdefault( strKO, [] ) ) + "_" + strKO + "|" + strOrg )
else:
	for strKO in setPaths:
		print( "|".join( hashMeta.setdefault( strKO, [] ) ) + "_" + strKO )
