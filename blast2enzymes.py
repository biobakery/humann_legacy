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
	raise Exception( "Usage: blast2enzymes.py <koc> [filter] [mblastx] < <blast.txt>" )
strKOC = sys.argv[1]
dFilter = 0 if ( len( sys.argv ) <= 2 ) else float(sys.argv[2])
fMBlastX = False if ( len( sys.argv ) <= 3 ) else ( int(sys.argv[3]) != 0 )

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
# Keep only hits that correspond to at least one KO
	aiScores = filter( lambda i: hashCOK.get( astrTos[pTos[i]].upper( ).replace( ":", "#", 1 ) ),
		apScores[iFrom] )
	dSum = sum( (pScores[i] for i in aiScores) )
	for iScore in aiScores:
		iCur, dCur = (pArray[iScore] for pArray in (pTos, pScores))
		strOrg, strGene = astrTos[iCur].split( ":" )
		strGene = strGene.upper( )
		hashGenes = hashhashOrgs.setdefault( strOrg, {} )
		hashGenes[strGene] = ( dCur / dSum ) + hashGenes.get(
			strGene, 0 )

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
