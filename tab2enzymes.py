#!/usr/bin/env python

import math
import re
import sys

if len( sys.argv ) != 2:
	raise Exception( "Usage: tab2enzymes.py <mockrefs.txt> < <blast.txt>" )
strMRs = sys.argv[1]

hashKOC = {}
setGenes = set()
for strLine in open( strMRs ):
	astrLine = strLine.rstrip( ).split( "\t" )
	strGene, astrKOs = astrLine[0], astrLine[1:]
	setGenes.add( strGene )
	for strKO in astrKOs:
		hashKOC.setdefault( strKO, set() ).add( strGene.upper( ) )
astrKOs = hashKOC.keys( )

hashGenes = {}
for strLine in sys.stdin:
	strLine = strLine.strip( )
	if strLine[0] == "#":
		continue
	astrLine = strLine.split( "\t" )
	strTo, strFrom, strID1, strID2 = (astrLine[i] for i in (0, 1, 5, 6))
	astrTo = strTo.split( "|" )
	if len( astrTo ) < 4:
		continue
	strTo = astrTo[3]
	if strTo not in setGenes:
		continue
	try:
		dID1 = float(strID1)
		dID2 = float(strID2)
	except ValueError:
		continue
	dScore = min( dID1, dID2 ) / 100
	hashGenes[strTo] = dScore + hashGenes.get( strTo, 0 )

hashScores = {}
dSum = 0
for strKO in astrKOs:
	dScore = sum( hashGenes.get( strGene, 0 ) for strGene in
		hashKOC.get( strKO, set() ) )
	if dScore > 0:
		hashScores[strKO] = dScore
		dSum += dScore

print( "GID	Abundance" )
for strKO, dScore in hashScores.items( ):
	print( "\t".join( (strKO, str(dScore)) ) ) # / dSum)) ) )
