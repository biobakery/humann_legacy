#!/usr/bin/env python

import random
import re
import sys

if len( sys.argv ) < 4:
	raise Exception( "Usage: mixer.py <bases> <stagger> <reads.txt>+ < <organisms.txt>" )
strBases, strStagger, astrReads = sys.argv[1], sys.argv[2], sys.argv[3:]
fStagger = int(strStagger) != 0
iBases = int(strBases)

hashReads = {}
for strReads in astrReads:
	pMatch = re.search( '^(?:.*\/)?(\S+?)(?:\.\S*)?$', strReads )
	if not pMatch:
		sys.stderr.write( "Illegal genome: %s\n" % strReads )
		continue
	hashReads[pMatch.group( 1 )] = strReads

dTotal = 0
hashStagger = {}
hashGenomes = {}
hashProvenance = {}
for strLine in sys.stdin:
	strLine = strLine.strip( )
	if strLine[0] == "#":
		continue
	strOrg, strStagger = strLine.split( "\t" )
	strReads = hashReads.get( strOrg )
	if not strReads:
		sys.stderr.write( "Unknown genome: %s\n" % strOrg )
		continue
	dStagger = float(strStagger) if fStagger else 1.0
	dTotal += dStagger
	hashStagger[strOrg] = dStagger
	hashGenomes[strOrg] = astrReads = []
	hashProvenance[strOrg] = astrProvenance = []
	strRead = strID = ""
	for strRLine in open( strReads ):
		strRLine = strRLine.lstrip( )
		if strRLine[0] == ">":
			if len( strRead ) > 0:
				astrProvenance.append( strID )
				astrReads.append( strRead.strip( ) )
			strID = strRLine[1:].strip( )
			strRead = ""
		else:
			strRead += strRLine

astrOrgs = []
adOrgs = []
for strOrg, dStagger in hashStagger.items( ):
	astrOrgs.append( strOrg )
	adOrgs.append( dStagger / dTotal )

iRead = 0
iOutput = 0
while( iOutput < iBases ):
	dOrg = random.random( )
	dSum = 0
	for iOrg in range( len( astrOrgs ) ):
		dSum += adOrgs[iOrg]
		if dOrg <= dSum:
			break
	strOrg = astrOrgs[iOrg]
	astrReads = hashGenomes[strOrg]
	iCur = random.randrange( len( astrReads ) )
	print( ">R%09d %s" % (iRead, hashProvenance[strOrg][iCur]) )
	print( astrReads[iCur] )
	iRead += 1
	iOutput += len( strRead )
