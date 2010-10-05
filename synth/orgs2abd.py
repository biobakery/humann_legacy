#!/usr/bin/env python

import re
import sys

c_strKO	= "ko"

if len( sys.argv ) < 3:
	raise Exception( "Usage: orgs2abd.py <stagger> <pathways.list>+ < <organisms.txt>" )
strStagger, astrPathways = sys.argv[1], sys.argv[2:]
fStagger = int(strStagger) != 0

hashOrgs = {}
hashHits = {}
for strLine in sys.stdin:
	strLine = strLine.strip( )
	if strLine[0] == "#":
		continue
	strOrg, strAbd = strLine.split( "\t" )
	hashOrgs[strOrg] = float(strAbd)
	hashHits[strOrg] = False

hashPathways = {}
for strPathways in astrPathways:
	pMatch = re.search( '^(?:.*\/)?([a-z]{3}?)_pathway\.list$', strPathways )
	if not pMatch:
		sys.stderr.write( "Illegal genome: %s\n" % strPathways )
		continue
	strOrg = pMatch.group( 1 )
	if strOrg not in hashOrgs:
		sys.stderr.write( "Extra genome: %s\n" % strPathways )
		continue
	hashHits[strOrg] = True
	hashPathways[strOrg] = setPathways = set()
	for strLine in open( strPathways ):
		strGene, strToken = strLine.strip( ).split( "\t" )
		strToken, strID = strToken.split( ":" )
		setPathways.add( strID[3:] )

for strOrg, fOrg in hashHits.items( ):
	if not fOrg:
		sys.stderr.write( "Missing genome: %s\n" % strOrg )

hashAbds = {}
for strOrg, setPathways in hashPathways.items( ):
	dAbd = hashOrgs[strOrg] if fStagger else 1
	for strPathway in setPathways:
		dCur = hashAbds.get( strPathway, 0 )
		hashAbds[strPathway] = dCur + dAbd

print( "PID	Abundance" )
for strPathway, dAbd in hashAbds.items( ):
	print( "\t".join( (c_strKO + strPathway, ( "%g" % dAbd ) ) ) )
	