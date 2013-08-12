#!/usr/bin/env python

"""
Description:
Point in the pipeline: Does not have a number for it in the file naming scheme, finalizer.
Program called before: filter.py (if called at all, not always called).
Program called after: eco.py (if called at all, not always called).
"""

import sys

astrIDs = adSums = None
aadData = []
fOrg = False
for strLine in sys.stdin:
	astrLine = strLine.split( "\t" )
	if ( astrLine[1] == "Organism" ) | fOrg:
		astrData = [strCur.strip( ) for strCur in astrLine[2:]]
	else:
		astrData = [strCur.strip( ) for strCur in astrLine[1:]]
	if adSums:
		if fOrg:
			astrIDs.append( ":".join( ( astrLine[0], astrLine[1] ) ) )
		else:
			astrIDs.append( astrLine[0] )
		adData = [( float(strCur) if ( len( strCur ) > 0 ) else None ) for
			strCur in astrData]
		aadData.append( adData )
		for i in range( len( adData ) ):
			if adData[i]:
				adSums[i] += adData[i]
	else:
		astrIDs = []
		fOrg = astrLine[1] == "Organism"
		adSums = [0] * len( astrData )
		print( strLine.strip( ) )

for iRow in range( len( astrIDs ) ):
	adData = aadData[iRow]
	for iCol in range( len( adSums ) ):
		if adData[iCol]:
			adData[iCol] /= adSums[iCol]
	if fOrg:
		astrID = astrIDs[iRow].split(":")
	else:
		astrID = [astrIDs[iRow]]
	print( "\t".join( astrID + [( "" if ( d == None ) else str(d) ) for d in
		adData] ) )
