#!/usr/bin/env python

import math
import sys

if len( sys.argv ) != 2:
	raise Exception( "Usage: blast2enzymes.py <koc> < <blast.txt>" )
strKOC = sys.argv[1]

hashKOC = {}
for strLine in open( strKOC ):
	astrLine = strLine.rstrip( ).split( "\t" )
	hashKOC[astrLine[0]] = hashKO = {}
	for strToken in astrLine[1:]:
		strOrg, strGene = strToken.split( "#" )
		hashKO.setdefault( strOrg.lower( ), set() ).add( strGene.upper( ) )

dSum = 0
strPrev = None
hashAlignments = {}
hashhashOrgs = {}
for strLine in sys.stdin:
	strLine = strLine.strip( )
	if strLine[0] == "#":
		continue
	astrLine = strLine.split( "\t" )
	strFrom = astrLine[2]
	if strFrom != strPrev:
		if dSum > 0:
#			sys.stderr.write( "%s\t%g\n" % (strFrom, dSum) )
			for strCur, dCur in hashAlignments.items( ):
				strOrg, strGene = strCur.split( ":" )
				strGene = strGene.upper( )
				hashGenes = hashhashOrgs.setdefault( strOrg, {} )
				hashGenes[strGene] = ( dCur / dSum ) + hashGenes.get(
					strGene, 0 )
		strPrev = strFrom
		dSum = 0
		hashAlignments = {}
	strTo, strScore = astrLine[0], astrLine[-1]
	if strTo.find( ":" ) < 0:
		continue
	try:
		dScore = float(strScore)
	except ValueError:
		continue
	dScore = math.exp( -dScore )
	dSum += dScore
	hashAlignments[strTo] = max( (hashAlignments.get( strTo, 0 ), dScore) )

astrOrgs = hashhashOrgs.keys( )
hashScores = {}
dSum = 0
for strKO, hashKO in hashKOC.items( ):
	adScores = [0] * len( astrOrgs )
	for i in range( len( adScores ) ):
		strOrg = astrOrgs[i]
		for strGene in hashKO.get( strOrg, set() ):
			adScores[i] += hashhashOrgs.get( strOrg, {} ).get( strGene, 0 )
	dScore = sum( adScores )
	if dScore > 0:
		hashScores[strKO] = dScore
		dSum += dScore

print( "GID	Abundance" )
for strKO, dScore in hashScores.items( ):
	print( "\t".join( (strKO, str(dScore)) ) ) # / dSum)) ) )
