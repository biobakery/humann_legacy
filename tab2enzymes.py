#!/usr/bin/env python

import math
import sys

if len( sys.argv ) != 2:
	raise Exception( "Usage: tab2enzymes.py <koc> < <blast.txt>" )
strKOC = sys.argv[1]

hashKOC = {}
astrKOs = []
for strLine in open( strKOC ):
	astrLine = strLine.rstrip( ).split( "\t" )
	astrKOs.append( astrLine[0] )
	for strToken in astrLine[1:]:
		strOrg, strGene = strToken.split( "#" )
		strOrg = strOrg.lower( )
		strGene = strGene.upper( )
		hashKOC.setdefault( strOrg, {} ).setdefault( astrLine[0],
			{} )[strGene] = True

strPrev = None
hashAlignments = {}
hashhashOrgs = {}
for strLine in sys.stdin:
	strLine = strLine.strip( )
	if strLine[0] == "#":
		continue
	astrLine = strLine.split( "\t" )
	strFrom, strTo, strScore = astrLine[2], astrLine[0], astrLine[-1]
	try:
		dScore = float(strScore)
	except ValueError:
		continue
	dScore = 1 - math.exp( -dScore )
	if strFrom != strPrev:
		adScores = (( 1 - d ) for d in hashAlignments.values( ))
		dSum = sum( adScores )
		if dSum > 0:
#			sys.stderr.write( "%s\t%g\n" % (strFrom, dSum) )
			for astrTo, dScore in hashAlignments.items( ):
				strOrg, strGene = astrTo
				strGene = strGene.upper( )
				d = ( 1 - dScore ) / dSum
				if strOrg in hashhashOrgs:
					hashGenes = hashhashOrgs[strOrg]
					d += hashGenes.get( strGene, 0 )
					hashGenes[strGene] = d
				else:
					hashhashOrgs[strOrg] = {strGene : d}

		strPrev = strFrom
		hashAlignments = {}
	if strTo.find( ":" ) < 0:
		continue
	strOrg, strID = strTo.split( ":" )
	astrTo = (strOrg, strID)
	hashAlignments[astrTo] = min( (hashAlignments.get( astrTo, 1 ), dScore) )

astrOrgs = hashhashOrgs.keys( )
hashScores = {}
dSum = 0
for strKO in astrKOs:
	adScores = [0] * len( astrOrgs )
	for i in range( len( adScores ) ):
		strOrg = astrOrgs[i]
		for strGene in hashKOC.get( strOrg, {} ).get( strKO, {} ).keys( ):
			adScores[i] += hashhashOrgs.get( strOrg, {} ).get( strGene, 0 )
	dScore = sum( adScores )
	if dScore > 0:
		hashScores[strKO] = dScore
		dSum += dScore

print( "GID	Abundance" )
for strKO, dScore in hashScores.items( ):
	print( "\t".join( (strKO, str(dScore)) ) ) # / dSum)) ) )
