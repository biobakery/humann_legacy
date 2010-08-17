#!/usr/bin/env python

import sys

c_dEpsilon	= 0.1

if len( sys.argv ) != 2:
	raise Exception( "Usage: smooth.py <keggc> < <pathways.txt>" )
strKEGGC = sys.argv[1]

hashKOs = {}
for strLine in open( strKEGGC ):
	astrLine = strLine.strip( ).split( "\t" )
	for strKO in astrLine[1:]:
		hashKOs.setdefault( strKO, [] ).append( astrLine[0] )

setHit = set()
for strLine in sys.stdin:
	strLine = strLine.strip( )
	astrLine = strLine.split( "\t" )
	if astrLine[0] == "GID":
		print( strLine )
		continue
	setHit.add( "_".join( astrLine[0:2] ) )
	astrLine[2] = str(float(astrLine[2]) + c_dEpsilon)
	print( "\t".join( astrLine ) )
for strKO, astrKEGGs in hashKOs.items( ):
	for strKEGG in astrKEGGs:
		if "_".join( (strKO, strKEGG) ) not in setHit:
			print( "\t".join( (strKO, strKEGG, str(c_dEpsilon)) ) )
