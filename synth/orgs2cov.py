#!/usr/bin/env python

import re
import sys

c_strKO	= "ko"

if len( sys.argv ) < 3:
	raise Exception( "Usage: orgs2cov.py <stagger> <pathways.list>+ < <organisms.txt>" )
strStagger, astrPathways = sys.argv[1], sys.argv[2:]

hashOrgs = {}
for strLine in sys.stdin:
	strLine = strLine.strip( )
	if strLine[0] == "#":
		continue
	hashOrgs[strLine.split( "\t" )[0]] = False

setPathways = set()
for strPathways in astrPathways:
	pMatch = re.search( '^(?:.*\/)?([a-z]{3}?)_pathway\.list$', strPathways )
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
		setPathways.add( strID[3:] )

for strOrg, fOrg in hashOrgs.items( ):
	if not fOrg:
		sys.stderr.write( "Missing genome: %s\n" % strOrg )

print( "PID	Coverage" )
for strPathway in setPathways:
	print( "\t".join( (c_strKO + strPathway, "1") ) )
	