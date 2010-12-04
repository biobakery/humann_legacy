#!/usr/bin/env python

import re
import sys

if len( sys.argv ) != 3:
	raise Exception( "Usage: orgs2kos.py <stagger> <koc> < <organisms.txt>" )
strStagger, strKOC = sys.argv[1:]
fStagger = int(strStagger) != 0

hashOrgs = {}
for strLine in sys.stdin:
	strLine = strLine.strip( )
	if strLine[0] == "#":
		continue
	strOrg, strAbd = strLine.split( "\t" )
	hashOrgs[strOrg] = float(strAbd)

hashKOs = {}
for strLine in open( strKOC ):
	astrLine = strLine.strip( ).split( "\t" )
	strKO = astrLine[0]
	for strToken in astrLine[1:]:
		strOrg, strGene = strToken.split( "#" )
		strOrg = strOrg.lower( )
		if ( strOrg in hashOrgs ):
			hashKOs.setdefault( strKO, set() ).add( strOrg )

print( "PID	Abundance" )
for strKO, setOrgs in hashKOs.items( ):
	dKO = 0
	for strOrg in setOrgs:
		dKO += hashOrgs[strOrg] if fStagger else 1
	if dKO:
		print( "\t".join( (strKO, ( "%g" % dKO ) ) ) )