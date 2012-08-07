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

for strLine in sys.stdin:
	if strLine and ( strLine[0] == "#" ):
		sys.stdout.write( strLine )
		continue
	astrLine = strLine.strip( ).split( "\t" )
	if astrLine[0] == "GID":
		fOrg = len(astrLine) > 2
		sys.stdout.write( "GID	" )
		if fOrg:
			sys.stdout.write( "Organism	" )
		print( "Pathway	Abundance" )
		continue
	astrKEGGs = hashKOs.get( astrLine[0] )
	if not astrKEGGs:
		print( astrLine[0] + "\t" )
		if fOrg:
			print( astrLine[1] + "\t\t" + astrLine[2] )
		else:
			print( "\t" + astrLine[1] )
		continue
#	adAbs = [random.random( ) for strCur in astrKEGGs]
#	dSum = sum( adAbs )
#	adAbs = [( dCur / dSum ) for dCur in adAbs]
	adAbs = [1] * len( astrKEGGs )
	for i in range( len( astrKEGGs ) ):
		if fOrg:
			print( "\t".join( (astrLine[0], astrLine[1], astrKEGGs[i], str(adAbs[i] * float( astrLine[2] ) ) ) ) )
		else:
			print( "\t".join( (astrLine[0], astrKEGGs[i], str(adAbs[i] * float( astrLine[2] ) ) ) ) )
