#!/usr/bin/env python

import array
import math
import sys

c_iLength	= 10

def enhash( strID, hashIDs, astrIDs, apScores = None ):
	
	iID = hashIDs.get( strID )
	if iID == None:
		hashIDs[strID] = iID = len( hashIDs )
		astrIDs.append( strID )
		if apScores != None:
			apScores.append( array.array( "L" ) )
		
	return iID

if len( sys.argv ) < 2:
	raise Exception( "Usage: blast2enzymes.py <koc> [genels] [filter] [mblastx] [topn] < <blast.txt>" )
strKOC = sys.argv[1]
strGeneLs = None if ( len( sys.argv ) <= 2 ) else sys.argv[2]
dFilter = 0 if ( len( sys.argv ) <= 3 ) else float(sys.argv[3])
fMBlastX = False if ( len( sys.argv ) <= 4 ) else ( int(sys.argv[4]) != 0 )
iTopN = -1 if ( len( sys.argv ) <= 5 ) else int(sys.argv[5])

hashGeneLs = {}
if strGeneLs:
	dAve = 0
	for strLine in open( strGeneLs ):
		strGene, strLength = strLine.strip( ).split( "\t" )
		hashGeneLs[strGene] = iLength = int(strLength)
		dAve += iLength
	dAve /= float(len( hashGeneLs ))
	for strGene, iLength in hashGeneLs.items( ):
		hashGeneLs[strGene] = iLength / dAve

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
for strLine in sys.stdin:
	strLine = strLine.rstrip( )
	if ( not strLine ) or ( strLine[0] == "#" ):
		continue
	astrLine = strLine.split( "\t" )
	if not astrLine[0]:
		continue
	try:
		strTo, strFrom, strID, strScore = (astrLine[1], astrLine[0], astrLine[4], astrLine[2]) \
			if fMBlastX else (astrLine[0], astrLine[2], astrLine[7], astrLine[-1])
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
	strFrom = strFrom[:c_iLength]
	iTo = enhash( strTo, hashTos, astrTos )
	iFrom = enhash( strFrom, hashFroms, astrFroms, apScores )
	iScore = len( pTos )
	apScores[iFrom].append( len( pTos ) )
	pTos.append( iTo )
	pScores.append( math.exp( -dScore ) )
hashhashOrgs = {}
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
		strOrg, strGene = strTo.split( ":" )
		strGene = strGene.upper( )
		hashGenes = hashhashOrgs.setdefault( strOrg, {} )
		hashGenes[strGene] = ( dCur / dSum ) + hashGenes.get( strGene, 0 )

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
