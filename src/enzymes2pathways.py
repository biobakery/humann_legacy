#!/usr/bin/env python

import random
import sys

if len( sys.argv ) != 2:
	raise Exception( "Usage: enzymes2pathways.py <keggc> < <enzymes.txt>" )
strKEGGC = sys.argv[1]

hashKOs = {}
for strLine in open( strKEGGC ):
	astrLine = strLine.strip( ).split( "\t" )
	for strKO in astrLine[1:]:
		hashKOs.setdefault( strKO, [] ).append( astrLine[0] )

print( "GID	Pathway	Abundance" )
for strLine in sys.stdin:
	if strLine and ( strLine[0] == "#" ):
		sys.stdout.write( strLine )
		continue
	astrLine = strLine.strip( ).split( "\t" )
	if astrLine[0] == "GID":
		continue
	strKO, dAb = astrLine[0], float(astrLine[1])
	astrKEGGs = hashKOs.get( strKO )
	if not astrKEGGs:
		print( strKO + "		" + astrLine[1] )
		continue
#	adAbs = [random.random( ) for strCur in astrKEGGs]
#	dSum = sum( adAbs )
#	adAbs = [( dCur / dSum ) for dCur in adAbs]
	adAbs = [1] * len( astrKEGGs )
	for i in range( len( astrKEGGs ) ):
		print( "\t".join( (strKO, astrKEGGs[i], str(adAbs[i] * dAb)) ) )
