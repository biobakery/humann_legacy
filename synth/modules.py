#!/usr/bin/env python

import sys

if len( sys.argv ) != 3:
	raise Exception( "Usage: modules.py <org> <koc> < <modulec>" )
strTarget, strKOC = sys.argv[1:]

setKOs = set()
for strLine in open( strKOC ):
	astrLine = strLine.strip( ).split( "\t" )
	for strToken in astrLine[1:]:
		strOrg, strGene = strToken.split( "#" )
		if strOrg.lower( ) == strTarget:
			setKOs.add( astrLine[0] )
			break

for strLine in sys.stdin:
	astrLine = strLine.strip( ).split( "\t" )
	fOK = True
	for strKO in astrLine[1:]:
		if strKO not in setKOs:
			fOK = False
			break
	if not fOK:
		continue
	for strKO in astrLine[1:]:
		print( "\t".join( (strKO, "path:" + astrLine[0]) ) )
