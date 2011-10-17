#!/usr/bin/env python

import array
import hits
import math
import re
import sys

def median( ad ):
	
	return ad[int(len( ad ) / 2)]

strGeneLs = None if ( len( sys.argv ) <= 1 ) else sys.argv[1]
if strGeneLs in ("-h", "-help", "--help"):
	raise Exception( "Usage: hits2metarep.py [genels] < <hits.bin>" )

pHits = hits.CHits( )
pHits.open( sys.stdin )

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

pAbundances = array.array( "f", (0 for i in range( pHits.get_tos( ) )) )
apScores = []
for i in range( pHits.get_tos( ) ):
	apScores.append( array.array( "L" ) )
for iFrom in range( pHits.get_froms( ) ):
	aiScores = pHits.get_scores( iFrom )
	aiTos = [pHits.get_scoreto( i ) for i in aiScores]
	aiIndices = filter( lambda i: pHits.get_to( aiTos[i] ).find( ":" ) >= 0, range( len( aiTos ) ) )
	aiScores, aiTos = ([a[i] for i in aiIndices] for a in (aiScores, aiTos))
	aadScores = [pHits.get_dic( i ) for i in aiScores]
	dSum = sum( math.exp( -a[0] ) for a in aadScores )
	for i in range( len( aiScores ) ):
		iTo, adCur = (a[i] for a in (aiTos, aadScores))
		strTo = pHits.get_to( iTo )
		strTo = re.sub( r'\s+.*$', "", strTo )
		dScore = math.exp( -adCur[0] ) / hashGeneLs.get( strTo, 1 )
		pAbundances[iTo] += dScore / ( dSum or 1 )
		apScores[iTo].append( aiScores[i] )

for iTo in range( len( pAbundances ) ):
	aadScores = [pHits.get_dic( i ) for i in apScores[iTo]]
	adScores = [median( sorted( aadScores[i][j] for i in range( len( aadScores ) ) ) ) for j in range( len( aadScores[0] ) )]
	print( "\t".join( [pHits.get_to( iTo )] + [( "%g" % d ) for d in ( [pAbundances[iTo]] +
		adScores )] ) )
