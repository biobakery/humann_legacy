#!/usr/bin/env python

import sys
import csv

astrHeaders = astrIDs = []
aadData = []
for strLine in sys.stdin:
	astrLine = strLine.rstrip( ).split( "\t" )
	strID, astrData = astrLine[0], astrLine[1:]
	if astrHeaders:
		astrIDs.append( strID )
		aadData.append( [float(s) for s in astrData] )
	else:
		astrHeaders = astrData

for iCol, strCol in enumerate( astrHeaders ):
	ostm = open( "output/" + strCol + "_01-keg.txt", "w" )
	ostm.write( "GID\tAbundance\n" )
	for iRow, strRow in enumerate( astrIDs ):
		ostm.write( "%s\t%g\n" % (strID, aadData[iRow][iCol]) )
