#!/usr/bin/env python

import sys

astrIDs = adSums = None
aadData = []
for strLine in sys.stdin:
	astrLine = strLine.split( "\t" )
	astrData = [strCur.strip( ) for strCur in astrLine[1:]]
	if adSums:
		astrIDs.append( astrLine[0] )
		adData = [( float(strCur) if ( len( strCur ) > 0 ) else None ) for
			strCur in astrData]
		aadData.append( adData )
		for i in range( len( adData ) ):
			if adData[i]:
				adSums[i] += adData[i]
	else:
		astrIDs = []
		adSums = [0] * len( astrData )
		print( strLine.strip( ) )

for iRow in range( len( astrIDs ) ):
	adData = aadData[iRow]
	for iCol in range( len( adSums ) ):
		if adData[iCol]:
			adData[iCol] /= adSums[iCol]
	print( "\t".join( [astrIDs[iRow]] + [( "" if ( d == None ) else str(d) ) for d in
		adData] ) )
