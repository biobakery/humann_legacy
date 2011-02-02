#!/usr/bin/env python

import pathway
import sys

c_fMedup	= True

if len( sys.argv ) < 2:
	raise Exception( "Usage: pathab.py <keggc> [modulep] [medup=" + str(c_fMedup) + "] < <pathways.txt>" )
strKEGGC = sys.argv[1]
strModuleP = None if ( len( sys.argv ) <= 2 ) else sys.argv[2]
fMedup = c_fMedup if ( len( sys.argv ) <= 3 ) else ( int(sys.argv[3]) != 0 )

hashKEGGs = {}
for strLine in open( strKEGGC ):
	astrLine = strLine.strip( ).split( "\t" )
	hashKEGGs[astrLine[0]] = astrLine[1:]

hashModules = {}
if strModuleP:
	for pPathway in pathway.open( open( strModuleP ) ):
		hashModules[pPathway.id( )] = pPathway

hashKOs = {}
hashScores = {}
for strLine in sys.stdin:
	strLine = strLine.strip( )
	astrLine = strLine.split( "\t" )
	if astrLine[0] == "GID":
		continue
	strKO, strKEGG, strScore = astrLine
	dScore = float(strScore)
	hashKOs[strKO] = max( dScore, hashKOs.get( strKO, 0 ) )
	hashScores.setdefault( strKEGG, {} )[strKO] = dScore
adScores = sorted( hashKOs.values( ) )
if len( adScores ) > 2:
	d25, d50, d75 = (adScores[int(round( 0.25 * ( i + 1 ) * len( adScores ) ))] for i in range( 3 ))
else:
	d25, d50, d75 = [adScores[0] if adScores else 0] * 3
print( "PID	Abundance" )
#sys.stderr.write( "%s\n" % "\t".join( ["PID", "Abundance"] + ( ["X"] * max( map( lambda a: len( a ), hashKEGGs.values( ) ) ) ) ) )
for strKEGG, hashKOs in hashScores.items( ):
	if len( strKEGG ) == 0:
		continue
	for strKO in hashKEGGs.get( strKEGG, [] ):
		hashKOs.setdefault( strKO, 0 )
	adAbs = sorted( hashKOs.values( ) )
#	dAb = adAbs[len( adAbs ) / 2] if fMedian else ( sum( adAbs ) / len( adAbs ) )
#	sys.stderr.write( "%s\n" % "\t".join( str(d) for d in ( [strKEGG] + adAbs ) ) )
	pPathway = hashModules.get( strKEGG )
	if pPathway:
		dAb = pPathway.abundance( hashKOs )
#		dAb = max( 0, sum( adAbs ) / len( adAbs ) - d50 )
	else:
		if fMedup:
			adAbs = adAbs[( len( adAbs ) / 2 ):]
		dAb = sum( adAbs ) / len( adAbs )
	print( "\t".join( (strKEGG, str(dAb)) ) )
