#!/usr/bin/env python

import sys

c_fMedup	= True
c_fSizer	= False

if len( sys.argv ) < 2:
	raise Exception( "Usage: pathab.py <keggc> [medup=" + str(c_fMedup) + "] [sizer=" + str(c_fSizer) + "] < <pathways.txt>" )
strKEGGC = sys.argv[1]
fMedup = c_fMedup if ( len( sys.argv ) <= 2 ) else ( int(sys.argv[2]) != 0 )
fSizer = c_fSizer if ( len( sys.argv ) <= 3 ) else ( int(sys.argv[3]) != 0 )

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
#sys.stderr.write( "%s\n" % "\t".join( ["PID", "Abundance"] + ( ["X"] * max( map( lambda a: len( a ), hashKEGGs.values( ) ) ) ) ) )
for strKEGG, hashKOs in hashScores.items( ):
	if len( strKEGG ) == 0:
		continue
	for strKO in hashKEGGs.get( strKEGG, [] ):
		hashKOs.setdefault( strKO, 0 )
	adAbs = sorted( hashKOs.values( ) )
#	dAb = adAbs[len( adAbs ) / 2] if fMedian else ( sum( adAbs ) / len( adAbs ) )
#	sys.stderr.write( "%s\n" % "\t".join( str(d) for d in ( [strKEGG] + adAbs ) ) )
	if fSizer:
		adTmp = adAbs[( len( adAbs ) / 2 ):]
		i = 5
		dAb = ( ( i * adAbs[0] ) + sum( adTmp ) ) / ( i + len( adTmp ) )
		if ( adAbs[-1] - dAb ) < dAb:
			dAb = max( 0, dAb - adAbs[0] )
	else:
		if fMedup:
			adAbs = adAbs[( len( adAbs ) / 2 ):]
		dAb = sum( adAbs ) / len( adAbs )
	print( "\t".join( (strKEGG, str(dAb)) ) )
