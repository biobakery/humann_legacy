#!/usr/bin/env python

import sys

if len( sys.argv ) != 2:
	raise Exception( "Usage: gapfill.py <keggc> < <pathways.txt>" )
strKEGGC = sys.argv[1]

hashKEGGs = {}
for strLine in open( strKEGGC ):
	astrLine = strLine.strip( ).split( "\t" )
	hashKEGGs[astrLine[0]] = astrLine[1:]

hashScores = {}
for strLine in sys.stdin:
	strLine = strLine.strip( )
	astrLine = strLine.split( "\t" )
	if astrLine[0] == "GID":
		print( strLine )
		continue
	hashScores.setdefault( astrLine[1], {} )[astrLine[0]] = float(astrLine[2])
for strKEGG, hashKOs in hashScores.items( ):
	adAbs = hashKOs.values( )
	adAbs.sort( )
	dAve = sum( adAbs ) / len( adAbs )
	if len( adAbs ) > 3:
		iFourth = len( adAbs ) / 4
		d25, d75 = adAbs[iFourth], adAbs[iFourth * 3]
		dIQR = d75 - d25
		dLIF = d25 - ( 1.5 * dIQR )
		for strKO, dAb in hashKOs.items( ):
			if dAb <= dLIF:
				hashKOs[strKO] = dAve
	for strKO, dAb in hashKOs.items( ):
		print( "\t".join( (strKO, strKEGG, str(dAb)) ) )
