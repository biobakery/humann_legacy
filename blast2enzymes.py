#!/usr/bin/env python

import array
import math
import sys

def enhash( strID, hashIDs, astrIDs, apScores = None ):
	
	iID = hashIDs.get( strID )
	if iID == None:
		hashIDs[strID] = iID = len( hashIDs )
		astrIDs.append( strID )
		if apScores != None:
			apScores.append( array.array( "L" ) )
		
	return iID

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

hashFroms = {}
hashTos = {}
astrTos = []
astrFroms = []
apScores = []
pTos = array.array( "L" )
pScores = array.array( "f" )
for strLine in sys.stdin:
	strLine = strLine.rstrip( )
	if strLine[0] == "#":
		continue
	astrLine = strLine.split( "\t" )
	strTo, strFrom, strScore = astrLine[0], astrLine[2], astrLine[-1]
	if strTo.find( ":" ) < 0:
		continue
	try:
		dScore = float(strScore)
	except ValueError:
		continue
	iTo = enhash( strTo, hashTos, astrTos )
	iFrom = enhash( strFrom, hashFroms, astrFroms, apScores )
	iScore = len( pTos )
	apScores[iFrom].append( len( pTos ) )
	pTos.append( iTo )
	pScores.append( math.exp( -dScore ) )
hashhashOrgs = {}
for iFrom in range( len( astrFroms ) ):
	"""
	c_iCutoff = 50
	if len( hashAlignments ) > c_iCutoff:
		adValues = sorted( hashAlignments.values( ), reverse = True )
		dCutoff = adValues[c_iCutoff]
		hashNew = {}
		for strCur, dCur in hashAlignments.items( ):
			if dCur > dCutoff:
				hashNew[strCur] = dCur
		hashAlignments = hashNew
	hashNew = {}
	for strCur, dCur in hashAlignments.items( ):
		if strCur.find( ":" ) >= 0:
			hashNew[strCur] = dCur
	hashAlignments = hashNew
	"""
	dSum = sum( (pScores[i] for i in apScores[iFrom]) )
#	sys.stderr.write( "%s\t%g\n" % (strFrom, dSum) )
	for iScore in apScores[iFrom]:
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
