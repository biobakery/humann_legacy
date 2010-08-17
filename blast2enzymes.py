#!/usr/bin/env python

import sys

if len( sys.argv ) != 2:
	raise Exception( "Usage: blast2enzymes.py <koc> < <blast.txt>" )
strKOC = sys.argv[1]

hashhashAlignments = {}
hashAlignments = None
for strLine in sys.stdin:
	if strLine[0] == "#":
		continue
	astrLine = strLine.rstrip( ).split( "\t" )
	strFrom, strTo, strScore = astrLine[2], astrLine[0], astrLine[-1]
	dScore = float(strScore)
	hashAlignments = hashhashAlignments.setdefault( strFrom, {} )
	strOrg, strID = strTo.split( ":" )
	a = (strOrg, strID)
	hashAlignments[a] = min( (hashAlignments.get( a, 1 ), dScore) )

hashhashOrgs = {}
for strFrom, hashAlignments in hashhashAlignments.items( ):
	adScores = (1 - d for d in hashAlignments.values( ))
	dSum = sum( adScores )
	if dSum == 0:
		continue
#	sys.stderr.write( "%s\t%g\n" % (strFrom, dSum) )
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

hashKOC = {}
astrKOs = []
for strLine in open( strKOC ):
	astrLine = strLine.rstrip( ).split( "\t" )
	astrKOs.append( astrLine[0] )
	for strToken in astrLine[1:]:
		strOrg, strGene = strToken.split( "#" )
		strOrg = strOrg.lower( )
		if not strOrg in hashhashOrgs:
			continue
		strGene = strGene.upper( )
		hashKOC.setdefault( strOrg, {} ).setdefault( astrLine[0],
			{} )[strGene] = True

astrOrgs = hashhashOrgs.keys( )
print( "GID	Abundance" )
for strKO in astrKOs:
	adScores = [0] * len( astrOrgs )
	for i in range( len( adScores ) ):
		strOrg = astrOrgs[i]
		for strGene in hashKOC.setdefault( strOrg, {} ).setdefault( strKO, {} ).keys( ):
			adScores[i] += hashhashOrgs.setdefault( strOrg, {} ).get(
				strGene, 0 )
	if sum( adScores ) == 0:
		continue
	print( "\t".join( (strKO, str(sum( adScores ))) ) )
