#!/usr/bin/env python

import sys

c_fMedian	= True

if len( sys.argv ) < 2:
	raise Exception( "Usage: pathcov.py <keggc> [median=" + str(c_fMedian) + "] < <pathways.txt>" )
strKEGGC = sys.argv[1]
fMedian = c_fMedian if ( len( sys.argv ) <= 2 ) else ( int(sys.argv[2]) != 0 )

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
if iAve:
	dAve /= iAve
adScores.sort( )
if adScores:
	dMed = adScores[len( adScores ) / 2] if fMedian else ( sum( adScores ) / len( adScores ) )
print( "PID	Coverage" )
for strKEGG, hashKOs in hashScores.items( ):
	if not ( strKEGG and hashKOs ):
		continue
	iHits = 0
	for strKO, dAb in hashKOs.items( ):
		if dAb > dMed:
			iHits += 1
	print( "\t".join( (strKEGG, str(float(iHits) / len( hashKOs ))) ) )
