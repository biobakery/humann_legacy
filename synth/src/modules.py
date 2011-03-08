#!/usr/bin/env python

import math
import pathway
import sys

c_dCov	= 1.01

if len( sys.argv ) != 3:
	raise Exception( "Usage: modules.py <org> <koc> < <modulep>" )
strTarget, strKOC = sys.argv[1:]

hashKOs = {}
for strLine in open( strKOC ):
	astrLine = strLine.strip( ).split( "\t" )
	for strToken in astrLine[1:]:
		strOrg, strGene = strToken.split( "#" )
		if strOrg.lower( ) == strTarget:
			hashKOs[astrLine[0]] = 1 + hashKOs.get( astrLine[0], 0 )

apPaths = pathway.open( sys.stdin )
for pPath in apPaths:
	dCov = pPath.coverage( hashKOs )
	if ( not dCov ) or ( pPath.size( ) * ( 1 - dCov ) ) > c_dCov:
		continue
	for strKO in pPath.genes( ):
		if hashKOs.get( strKO ):
			print( "\t".join( (strKO, "path:" + pPath.id( )) ) )
