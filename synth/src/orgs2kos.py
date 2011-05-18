#!/usr/bin/env python

import re
import sys

if len( sys.argv ) < 3:
	raise Exception( "Usage: orgs2kos.py <stagger> <koc> [kos] < <organisms.txt>" )
strStagger, strKOC = sys.argv[1:3]
strKOs = sys.argv[3] if ( len( sys.argv ) > 3 ) else None
fStagger = int(strStagger) != 0

hashOrgs = {}
for strLine in sys.stdin:
	strLine = strLine.strip( )
	if strLine[0] == "#":
		continue
	strOrg, strAbd = strLine.split( "\t" )
	hashOrgs[strOrg] = float(strAbd)

setstrKOs = set()
if strKOs:
	for strLine in open( strKOs ):
		setstrKOs.add( strLine.strip( ) )

hashKOs = {}
for strLine in open( strKOC ):
	astrLine = strLine.strip( ).split( "\t" )
	hashKOs[astrLine[0]] = hashKO = {}
	strKO = astrLine[0]
	if setstrKOs and ( strKO not in setstrKOs ):
		continue
	for strToken in astrLine[1:]:
		strOrg, strGene = strToken.split( "#" )
		strOrg = strOrg.lower( )
		if strOrg in hashOrgs:
			hashKO[strOrg] = hashKO.get( strOrg, 0 ) + 1

print( "PID	Abundance" )
for strKO, hashKO in hashKOs.items( ):
	dKO = 0
	for strOrg, iCopies in hashKO.items( ):
		dKO += ( hashOrgs[strOrg] if fStagger else 1 ) * iCopies
	if dKO:
		print( "\t".join( (strKO, ( "%g" % dKO ) ) ) )
