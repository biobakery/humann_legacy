#!/usr/bin/env python

import hits
import sys
import re

if len( sys.argv ) < 2:
	raise Exception( "Usage: pathways2graphlan.py <ko-lefse> < <input.txt>" )
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
	astrLine = strLine.rstrip( ).split( "|" )
	strKO = astrLine[-1].split( "_" )[-1]
	hashMeta[strKO] = strLine.rstrip( )

if fOrg:
	for ( strKO, strOrg ) in setPaths:
		print( hashMeta.get( strKO, strKO ) + "." + strOrg ) # Changed separator from pipe to period to reflect change from lefse to graphlan format.
else:
	for strKO in setPaths:
		print( hashMeta.get( strKO, strKO ) )
