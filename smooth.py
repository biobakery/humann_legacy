#!/usr/bin/env python

import sys

c_dEpsilon	= 0.1

if len( sys.argv ) != 2:
	raise Exception( "Usage: smooth.py <keggc> < <pathways.txt>" )
strKEGGC = sys.argv[1]

hashKEGGs = {}
for strLine in open( strKEGGC ):
	astrLine = strLine.strip( ).split( "\t" )
	hashKEGGs[astrLine[0]] = astrLine[1:]

setKEGGs = set()
setHit = set()
for strLine in sys.stdin:
	strKO, strKEGG, strScore = strLine.strip( ).split( "\t" )
	if strKO == "GID":
		sys.stdout.write( strLine )
		continue
	setKEGGs.add( strKEGG )
	setHit.add( "_".join( (strKO, strKEGG) ) )
	strScore = str(float(strScore) + c_dEpsilon)
	print( "\t".join( (strKO, strKEGG, strScore) ) )
for strKEGG in setKEGGs:
	for strKO in hashKEGGs.get( strKEGG, () ):
		if "_".join( (strKO, strKEGG) ) not in setHit:
			print( "\t".join( (strKO, strKEGG, str(c_dEpsilon)) ) )
