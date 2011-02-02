#!/usr/bin/env python

import array
import math
import sys

c_strID		= "%identical"

def enhash( strID, hashIDs, astrIDs, apScores = None ):
	
	iID = hashIDs.get( strID )
	if iID == None:
		hashIDs[strID] = iID = len( hashIDs )
		astrIDs.append( strID )
		if apScores != None:
			apScores.append( array.array( "L" ) )
		
	return iID

if len( sys.argv ) < 2:
	raise Exception( "Usage: blast2enzymes.py <koc> [genels] [type={blastx,mblastx,mapx}] [filter] [topn] < <blast.txt>" )
strKOC = sys.argv[1]
strGeneLs = None if ( len( sys.argv ) <= 2 ) else sys.argv[2]
strType = "blastx" if ( len( sys.argv ) <= 3 ) else sys.argv[3]
dFilter = 0 if ( len( sys.argv ) <= 4 ) else float(sys.argv[4])
iTopN = -1 if ( len( sys.argv ) <= 5 ) else int(sys.argv[5])

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

hashFroms = {}
hashTos = {}
astrTos = []
astrFroms = []
apScores = []
pTos = array.array( "L" )
pScores = array.array( "f" )
iID = 2 if ( strType == "blastx" ) else ( 4 if ( strType == "mblastx" ) else None )
for strLine in sys.stdin:
	strLine = strLine.rstrip( )
	if not strLine:
		continue
	astrLine = strLine.split( "\t" )
	if not astrLine[0]:
		continue
	if strLine[0] == "#":
		if iID == None:
			for i in range( len( astrLine ) ):
				if astrLine[i] == c_strID:
					iID = i
					break
		continue
	if iID == None:
		continue
	try:
		if strType == "mblastx":
			strTo, strFrom, strID, strScore = (astrLine[1], astrLine[0], astrLine[iID], astrLine[2])
		elif strType == "mapx":
			strTo, strFrom, strID, strScore = (astrLine[0], astrLine[2], astrLine[iID], astrLine[-1])
		else:
			strTo, strFrom, strID, strScore = (astrLine[1], astrLine[0], astrLine[iID], astrLine[-2])
	except IndexError:
		sys.stderr.write( "%s\n" % astrLine )
		continue
	if strTo.find( ":" ) < 0:
		continue
	try:
		dScore = float(strScore)
	except ValueError:
		continue
	if dFilter:
		dID = float(strID) / 100
		if ( dFilter > 0 ) and ( dID >= dFilter ):
			continue
	iTo = enhash( strTo, hashTos, astrTos )
	iFrom = enhash( strFrom, hashFroms, astrFroms, apScores )
	iScore = len( pTos )
	apScores[iFrom].append( len( pTos ) )
	pTos.append( iTo )
	pScores.append( math.exp( -dScore ) )
hashhashOrgs = {}
hashOrgs = {}
for iFrom in range( len( astrFroms ) ):
	aiScores = apScores[iFrom]
	if iTopN > 0:
		aiScores = sorted( aiScores, lambda iOne, iTwo: cmp( pScores[iTwo], pScores[iOne] ) )
		aiScores = aiScores[:iTopN]
# Keep only hits that correspond to at least one KO
	aiScores = filter( lambda i: hashCOK.get( astrTos[pTos[i]].upper( ).replace( ":", "#", 1 ) ),
		aiScores )
	dSum = sum( (pScores[i] for i in aiScores) )
	for iScore in aiScores:
		iCur, dCur = (pArray[iScore] for pArray in (pTos, pScores))
		strTo = astrTos[iCur]
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
