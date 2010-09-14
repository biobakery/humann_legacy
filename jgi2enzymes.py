#!/usr/bin/env python

import math
import sys

if len( sys.argv ) != 2:
	raise Exception( "Usage: jgi2enzymes.py <cogc> < <jgi.txt>" )
strCOGC = sys.argv[1]

hashCOGC = {}
astrKOs = []
for strLine in open( strCOGC ):
	astrLine = strLine.rstrip( ).split( "\t" )
	astrKOs.append( astrLine[0] )
	for strGene in astrLine[1:]:
		hashCOGC.setdefault( astrLine[0], set() ).add( strGene )

hashCOGs = {}
for strLine in sys.stdin:
	astrLine = strLine.strip( ).split( "\t" )
	if len( astrLine ) <= 10:
		continue
	strTos, strScore = astrLine[8], astrLine[10]
	try:
		dScore = float(strScore)
	except ValueError:
		continue
	if dScore >= 1:
		continue
	astrCOGs = []
	for strTo in strTos.split( "||" ):
		if strTo[0:3] == "COG":
			astrCOGs.append( strTo )
	for strCOG in astrCOGs:
		hashCOGs[strCOG] = hashCOGs.get( strCOG, 0 ) + ( 1.0 /
			len( astrCOGs ) )

hashScores = {}
dSum = 0
for strKO in astrKOs:
	astrCOGs = hashCOGC.get( strKO )
	if not astrCOGs:
		continue
	dScore = sum( (hashCOGs.get( strCOG, 0 ) for strCOG in astrCOGs) )
	if dScore > 0:
		dScore /= len( astrCOGs )
		hashScores[strKO] = dScore
		dSum += dScore

print( "GID	Abundance" )
for strKO, dScore in hashScores.items( ):
	print( "\t".join( (strKO, str(dScore)) ) ) # / dSum)) ) )
