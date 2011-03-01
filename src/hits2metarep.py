#!/usr/bin/env python

import array
import hits
import math
import sys

def median( ad ):
	
	return ad[int(len( ad ) / 2)]

pHits = hits.CHits( )
pHits.open( sys.stdin )

strGeneLs = None if ( len( sys.argv ) <= 1 ) else sys.argv[1]
if strGeneLs in ("-h", "-help", "--help"):
	raise Exception( "Usage: hits2metarep.py [genels] < <hits.bin>" )

hashGeneLs = {}
if strGeneLs:
	astrGenes = []
	aiGenes = []
	dAve = 0
	for strLine in open( strGeneLs ):
		strGene, strLength = strLine.strip( ).split( "\t" )
		astrGenes.append( strGene )
		iLength = int(strLength)
		aiGenes.append( iLength )
		dAve += iLength
	dAve /= float(len( astrGenes ))
	for i in range( len( astrGenes ) ):
		hashGeneLs[astrGenes[i]] = aiGenes[i] / dAve

pAbundances = array.array( "f" )
pEs = array.array( "f" )
pIDs = array.array( "f" )
pCovs = array.array( "f" )
hashGenes = {}
for iFrom in range( pHits.get_froms( ) ):
	strFrom = pHits.get_from( iFrom )
	aiScores = pHits.get_scores( iFrom )
	aiScores = filter( lambda i: pHits.get_to( pHits.get_scoreto( i ) ).find( ":" ) >= 0, aiScores )
	astrTos = [pHits.get_to( pHits.get_scoreto( i ) ) for i in aiScores]
	aadScores = [pHits.get_dic( i ) for i in aiScores]
	dSum = sum( math.exp( -a[0] ) for a in aadScores )
	for i in range( len( astrTos ) ):
		strTo, adCur = (a[i] for a in (astrTos, aadScores))
		dScore = math.exp( -adCur[0] ) / hashGeneLs.get( strTo, 1 )
		iTo = len( pAbundances )
		hashGenes.setdefault( strTo, [] ).append( iTo )
		pAbundances.append( dScore / dSum )
		pEs.append( adCur[0] )
		pIDs.append( adCur[1] )
		pCovs.append( adCur[2] )

for strGene, aiTos in hashGenes.items( ):
	adScores = [median( sorted( p[i] for i in aiTos ) ) for p in (pEs, pIDs, pCovs)]
	print( "\t".join( [strGene] + [( "%g" % d ) for d in
		( [sum( pAbundances[i] for i in aiTos )] + adScores )] ) )
