#!/usr/bin/env python

import re
import sys

c_strKO	= "ko"

if len( sys.argv ) < 4:
	raise Exception( "Usage: orgs2cov.py <stagger> <pathwayc> <pathways.list>+ < <organisms.txt>" )
strStagger, strPathways, astrPathways = sys.argv[1], sys.argv[2], sys.argv[3:]

hashOrgs = {}
for strLine in sys.stdin:
	strLine = strLine.strip( )
	if strLine[0] == "#":
		continue
	hashOrgs[strLine.split( "\t" )[0]] = False

hashPathways = {}
for strLine in open( strPathways ):
	astrLine = strLine.strip( ).split( "\t" )
	hashPathways[astrLine[0]] = True

for strPathways in astrPathways:
	pMatch = re.search( '^(?:.*\/)?([a-z]{3}?)_\S+\.list$', strPathways )
	if not pMatch:
		sys.stderr.write( "Illegal genome: %s\n" % strPathways )
		continue
	strOrg = pMatch.group( 1 )
	if strOrg not in hashOrgs:
		sys.stderr.write( "Extra genome: %s\n" % strPathways )
		continue
	hashOrgs[strOrg] = True
	for strLine in open( strPathways ):
		strGene, strPath = strLine.strip( ).split( "\t" )
		strPath, strID = strPath.split( ":" )
		mtch = re.search( '^[a-z]{3}(\d+)$', strID )
		if mtch:
			strID = c_strKO + mtch.group( 1 )
		if hashPathways.get( strID ):
			hashPathways[strID] = False

for strOrg, fOrg in hashOrgs.items( ):
	if not fOrg:
		sys.stderr.write( "Missing genome: %s\n" % strOrg )

print( "PID	Coverage" )
for strPathway, fAbsent in hashPathways.items( ):
	print( "\t".join( (strPathway, str(0 if fAbsent else 1)) ) )
