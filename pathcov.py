#!/usr/bin/env python

import sys

if len( sys.argv ) != 2:
	raise Exception( "Usage: pathcov.py <keggc> < <pathways.txt>" )
strKEGGC = sys.argv[1]

hashKEGGs = {}
for strLine in open( strKEGGC ):
	astrLine = strLine.strip( ).split( "\t" )
	hashKEGGs[astrLine[0]] = astrLine[1:]

dAve = iAve = 0
adScores = []
hashScores = {}
for strLine in sys.stdin:
	strLine = strLine.strip( )
	astrLine = strLine.split( "\t" )
	if astrLine[0] == "GID":
		continue
	dAb = float(astrLine[2])
	adScores.append( dAb )
	dAve += dAb
	iAve += 1
	hashScores.setdefault( astrLine[1], {} )[astrLine[0]] = dAb
dAve /= iAve
adScores.sort( )
dMed = adScores[len( adScores ) / 2]
print( "PID	Coverage" )
for strKEGG, hashKOs in hashScores.items( ):
	if len( strKEGG ) == 0:
		continue
	iHits = 0
	for strKO, dAb in hashKOs.items( ):
		if dAb >= dMed:
			iHits += 1
	print( "\t".join( (strKEGG, str(float(iHits) / len( hashKOs ))) ) )
