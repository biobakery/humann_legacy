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
	raise Exception( "Usage: blast2metacyc.py <mcc> [type={blastx,mblastx,mapx}] [filter] [topn] < <blast.txt>" )
strMCC = sys.argv[1]
strType = "blastx" if ( len( sys.argv ) <= 2 ) else sys.argv[2]
dFilter = 0 if ( len( sys.argv ) <= 3 ) else float(sys.argv[3])
iTopN = -1 if ( len( sys.argv ) <= 4 ) else int(sys.argv[4])

hashCCM = {}
hashMCC = {}
for strLine in open( strMCC ):
	astrLine = strLine.rstrip( ).split( "\t" )
	strID, astrGenes = astrLine[0], astrLine[1:]
	hashMCC[strID] = astrGenes
	for strGene in astrGenes:
		hashCCM.setdefault( strGene, set() ).add( strID )

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
	if strLine[0] == "#":
		if iID == None:
			for i in range( len( astrLine ) ):
				if astrLine[i] == c_strID:
					iID = i
					break
		continue
	if ( iID == None ) or ( not astrLine[0] ):
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
	if strTo not in hashCCM:
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
hashGenes = {}
for iFrom in range( len( astrFroms ) ):
	aiScores = apScores[iFrom]
	if iTopN > 0:
		aiScores = sorted( aiScores, lambda iOne, iTwo: cmp( pScores[iTwo], pScores[iOne] ) )
		aiScores = aiScores[:iTopN]
# Keep only hits that correspond to at least one reaction
	aiScores = filter( lambda i: hashCCM.get( astrTos[pTos[i]] ), aiScores )
	dSum = sum( (pScores[i] for i in aiScores) )
	for iScore in aiScores:
		iCur, dCur = (pArray[iScore] for pArray in (pTos, pScores))
		strGene = astrTos[iCur]
		hashGenes[strGene] = ( dCur / dSum ) + hashGenes.get( strGene, 0 )

hashScores = {}
dSum = 0
for strMC, astrGenes in hashMCC.items( ):
	dScore = 0
	for strGene in astrGenes:
		dScore += hashGenes.get( strGene, 0 )
	if dScore > 0:
		hashScores[strMC] = dScore
		dSum += dScore

print( "GID	Abundance" )
for strMC, dScore in hashScores.items( ):
	print( "\t".join( (strMC, str(dScore)) ) ) # / dSum)) ) )
