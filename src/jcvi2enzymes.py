#!/usr/bin/env python

import math
import sys

if len( sys.argv ) != 2:
	raise Exception( "Usage: jcvi2enzymes.py <ecc> < <jcvi.txt>" )
strECC = sys.argv[1]

hashECC = {}
astrKOs = []
for strLine in open( strECC ):
	astrLine = strLine.rstrip( ).split( "\t" )
	astrKOs.append( astrLine[0] )
	for strGene in astrLine[1:]:
		hashECC.setdefault( astrLine[0], set() ).add( strGene )

hashECs = {}
for strLine in sys.stdin:
	astrLine = strLine.strip( ).split( "\t" )
	if len( astrLine ) <= 11:
		continue
	strTo = astrLine[11]
	if len( strTo ) > 0:
		hashECs[strTo] = hashECs.get( strTo, 0 ) + 1.0

hashScores = {}
dSum = 0
for strKO in astrKOs:
	astrECs = hashECC.get( strKO )
	if not astrECs:
		continue
	dScore = sum( (hashECs.get( strEC, 0 ) for strEC in astrECs) )
	iScore = len( astrECs )
	for strEC in astrECs:
		astrEC = strEC.split( "." )
		astrEC[-1] = "-"
		d = hashECs.get( ".".join( astrEC ) )
		if d:
			iScore += 1
			dScore += d
	if dScore > 0:
		dScore /= iScore
		hashScores[strKO] = dScore
		dSum += dScore

print( "GID	Abundance" )
for strKO, dScore in hashScores.items( ):
	print( "\t".join( (strKO, str(dScore)) ) ) # / dSum)) ) )
