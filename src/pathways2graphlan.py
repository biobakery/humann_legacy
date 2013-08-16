#!/usr/bin/env python

import sys
import re

if len( sys.argv ) < 2:
	raise Exception( "Usage: pathways2graphlan.py <KEGG-graphlan> < <input.txt>" )
strKEGGc = sys.argv[1]

iLine = 4
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
for strLine in open( strKEGGc ):
	astrLine = strLine.rstrip( ).split( "|" )
	strKEGG = astrLine[-1].split( "_" )[-1]
	hashMeta[strKEGG] = strLine.rstrip( )

if fOrg:
	for ( strKEGG, strOrg ) in setPaths:
		print( hashMeta.get( strKEGG, strKEGG ) + "_" + strOrg )
else:
	for strKEGG in setPaths:
		print( hashMeta.get( strKEGG, strKEGG ) )
