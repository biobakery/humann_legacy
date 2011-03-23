#!/usr/bin/env python

import math
import pathway
import sys

# Used for coverage calculation + cutoff
c_dCov	= 0.5

if len( sys.argv ) != 3:
	raise Exception( "Usage: modules.py <org> <koc> < <modulep>" )
strTarget, strKOC = sys.argv[1:]

hashKOs = {}
setstrKOs = set()
for strLine in open( strKOC ):
	astrLine = strLine.strip( ).split( "\t" )
	setstrKOs.add( astrLine[0] )
	for strToken in astrLine[1:]:
		strOrg, strGene = strToken.split( "#" )
		if strOrg.lower( ) == strTarget:
			hashKOs[astrLine[0]] = 1 + hashKOs.get( astrLine[0], 0 )
# Provides some smoothing for one or two missing genes in big pathways 
dDefault = 1.0 / sum( hashKOs.values( ) )
for strKO in setstrKOs:
	hashKOs[strKO] = max( dDefault, hashKOs.get( strKO, 0 ) )

apPaths = pathway.open( sys.stdin )
for pPath in apPaths:
	dCov = pPath.coverage( hashKOs, c_dCov )
	if dCov < c_dCov:
		continue
	for strKO in pPath.genes( ):
		if hashKOs.get( strKO, 0 ) > dDefault:
			print( "\t".join( (strKO, "path:" + pPath.id( )) ) )
