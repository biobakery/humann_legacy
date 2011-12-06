#!/usr/bin/env python

import hits
import math
import re
import sys

c_strWeightPValue	= "pvalue"
c_strWeightBitScore	= "bitscore"
c_strWeightInvE		= "inve"
c_strWeightSigmoid	= "sigmoid"
c_strWeight			= c_strWeightPValue
c_dEpsilon			= 1e-20

def funcWeight( dValue, strWeight ):
	
	dRet = dValue
	if strWeight == c_strWeightPValue:
		dRet = math.exp( -dValue )
	elif strWeight == c_strWeightBitScore:
		dRet = max( c_dEpsilon, -math.log( max( c_dEpsilon, dValue ) ) )
	elif strWeight == c_strWeightInvE:
		dRet = 1.0 / max( c_dEpsilon, dValue )
	else:
		dRet = 1.0 / ( 1 + math.exp( dValue ) )
	return dRet

if len( sys.argv ) < 2:
	raise Exception( "Usage: hits2enzymes.py <koc> [genels] [topn] [weight] < <hits.bin>" )
strKOC = sys.argv[1]
strGeneLs = None if ( len( sys.argv ) <= 2 ) else sys.argv[2]
iTopN = -1 if ( len( sys.argv ) <= 3 ) else int(sys.argv[3])
strWeight = c_strWeight if ( len( sys.argv ) <= 4 ) else sys.argv[4]

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

hashCOK = {}
hashKOC = {}
for strLine in open( strKOC ):
	astrLine = strLine.rstrip( ).split( "\t" )
	hashKOC[astrLine[0]] = hashKO = {}
	for strToken in astrLine[1:]:
		hashCOK.setdefault( strToken, set() ).add( astrLine[0] )
		strOrg, strGene = strToken.split( "#" )
		hashKO.setdefault( strOrg.lower( ), set() ).add( strGene.upper( ) )

pHits = hits.CHits( )
pHits.open( sys.stdin )
hashhashOrgs = {}
hashOrgs = {}
for iFrom in range( pHits.get_froms( ) ):
	strFrom = pHits.get_from( iFrom )
	aiScores = pHits.get_scores( iFrom )
	aiScores = filter( lambda i: pHits.get_to( pHits.get_scoreto( i ) ).find( ":" ) >= 0, aiScores )
	if iTopN > 0:
		aiScores = sorted( aiScores, lambda iOne, iTwo: cmp( pHits.get_dic( iOne )[0], pHits.get_dic( iTwo )[0] ) )
		aiScores = aiScores[:iTopN]
	astrTos = [re.sub( r'\s+.*$', "", pHits.get_to( pHits.get_scoreto( i ) ) ) for i in aiScores]
# Keep only hits that correspond to at least one KO
	aiTmp = filter( lambda i: hashCOK.get( astrTos[i].upper( ).replace( ":", "#", 1 ) ),
		range( len( astrTos ) ) )
	aiScores, astrTos = ([a[i] for i in aiTmp] for a in (aiScores, astrTos))
	adScores = [funcWeight( pHits.get_dic( i )[0], strWeight ) for i in aiScores]
	dSum = max( c_dEpsilon, sum( adScores ) )
	for i in range( len( astrTos ) ):
		strTo, dCur = (a[i] for a in (astrTos, adScores))
		dCur /= hashGeneLs.get( strTo, 1 )
		d = dCur / dSum
		strOrg, strGene = strTo.split( ":" )
		hashOrgs[strOrg] = d + hashOrgs.get( strOrg, 0 )
		strGene = strGene.upper( )
		hashGenes = hashhashOrgs.setdefault( strOrg, {} )
		hashGenes[strGene] = d + hashGenes.get( strGene, 0 )

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
for strOrg, dScore in hashOrgs.items( ):
	print( "\t".join( ("#", strOrg, "%g" % dScore) ) )
for strKO, dScore in hashScores.items( ):
	print( "\t".join( (strKO, "%g" % dScore) ) ) # / dSum)) ) )
