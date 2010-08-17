#!/usr/bin/env python

import sys

if len( sys.argv ) != 2:
	raise Exception( "Usage: blast2enzymes.py <koc> < <blast.txt>" )
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
	astrLine = strLine.rstrip( ).split( "\t" )
	strFrom, strTo, strScore = astrLine[2], astrLine[0], astrLine[-1]
	try:
		dScore = float(strScore)
	except ValueError:
		continue
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
	strOrg, strID = strTo.split( ":" )
	a = (strOrg, strID)
	hashAlignments[a] = min( (hashAlignments.get( a, 1 ), dScore) )

astrOrgs = hashhashOrgs.keys( )
print( "GID	Abundance" )
for strKO in astrKOs:
#	sys.stderr.write( "%s\n" % strKO )
	adScores = [0] * len( astrOrgs )
	for i in range( len( adScores ) ):
		strOrg = astrOrgs[i]
		for strGene in hashKOC.get( strOrg, {} ).get( strKO, {} ).keys( ):
			adScores[i] += hashhashOrgs.get( strOrg, {} ).get( strGene, 0 )
	if sum( adScores ) == 0:
		continue
	print( "\t".join( (strKO, str(sum( adScores ))) ) )
