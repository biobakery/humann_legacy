#!/usr/bin/env python

import sys

if len( sys.argv ) != 2:
	raise Exception( "Usage: pathab.py <keggc> < <pathways.txt>" )
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
		continue
	strKO, strKEGG, strScore = astrLine
	hashScores.setdefault( strKEGG, {} )[strKO] = float(strScore)
print( "PID	Abundance" )
for strKEGG, hashKOs in hashScores.items( ):
	if len( strKEGG ) == 0:
		continue
	adAbs = hashKOs.values( )
	print( "\t".join( (strKEGG, str(sum(adAbs) / len( adAbs ))) ) )
