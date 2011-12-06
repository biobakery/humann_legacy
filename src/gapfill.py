#!/usr/bin/env python

import sys

c_dIQRs		= 1.5
c_fMedian	= True

if len( sys.argv ) < 2:
	raise Exception( "Usage: gapfill.py <keggc> [iqrs=" + str(c_dIQRs) + "] [median=" +
		str(c_fMedian) + "] < <pathways.txt>" )
strKEGGC = sys.argv[1]
dIQRs = c_dIQRs if ( len( sys.argv ) <= 2 ) else float(sys.argv[2])
fMedian = c_fMedian if ( len( sys.argv ) <= 3 ) else ( int(sys.argv[3]) != 0 )

hashKEGGs = {}
for strLine in open( strKEGGC ):
	astrLine = strLine.strip( ).split( "\t" )
	hashKEGGs[astrLine[0]] = astrLine[1:]

hashScores = {}
for strLine in sys.stdin:
	strLine = strLine.strip( )
	astrLine = strLine.split( "\t" )
	if astrLine[0] == "GID":
		print( strLine )
		continue
	hashScores.setdefault( astrLine[1], {} )[astrLine[0]] = float(astrLine[2])
for strKEGG, hashKOs in hashScores.items( ):
	adAbs = sorted( hashKOs.values( ) )
	if len( adAbs ) > 3:
		d25, d50, d75 = (adAbs[int(round( 0.25 * i ))] for i in (1, 2, 3))
		dIQR = d75 - d25
		dAve = dStd = 0
		for d in adAbs:
			dAve += d
			dStd += d * d
		dAve /= len( adAbs )
		dStd = ( ( dStd / ( len( adAbs ) - 1 ) ) - ( dAve * dAve ) )**0.5
		if fMedian:
			dLF = d50 - ( dIQRs * dIQR )
			dFill = dLF
		else:
			dLF = dAve - ( dIQRs * dStd )
			dFill = dLF

		for strKO, dAb in hashKOs.items( ):
			if dAb < dLF:
				hashKOs[strKO] = dFill
	for strKO, dAb in hashKOs.items( ):
		print( "\t".join( (strKO, strKEGG, str(dAb)) ) )
