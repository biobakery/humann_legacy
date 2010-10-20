#!/usr/bin/env python

import sys

c_fMedup	= True

if len( sys.argv ) < 2:
	raise Exception( "Usage: pathab.py <keggc> [medup=" + str(c_fMedup) + "] < <pathways.txt>" )
strKEGGC = sys.argv[1]
fMedup = c_fMedup if ( len( sys.argv ) <= 2 ) else ( int(sys.argv[2]) != 0 )

hashKEGGs = {}
for strLine in open( strKEGGC ):
	astrLine = strLine.strip( ).split( "\t" )
	hashKEGGs[astrLine[0]] = astrLine[1:]

hashScores = {}
for strLine in sys.stdin:
	strLine = strLine.strip( )
	astrLine = strLine.split( "\t" )
	if astrLine[0] == "GID":
		continue
	strKO, strKEGG, strScore = astrLine
	hashScores.setdefault( strKEGG, {} )[strKO] = float(strScore)
print( "PID	Abundance" )
for strKEGG, hashKOs in hashScores.items( ):
	if len( strKEGG ) == 0:
		continue
	adAbs = sorted( hashKOs.values( ) )
#	dAb = adAbs[len( adAbs ) / 2] if fMedian else ( sum( adAbs ) / len( adAbs ) )
	if fMedup:
		adAbs = adAbs[( len( adAbs ) / 2 ):]
	dAb = sum( adAbs ) / len( adAbs )
	print( "\t".join( (strKEGG, str(dAb)) ) )
