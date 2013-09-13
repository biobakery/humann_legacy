#!/usr/bin/env python

import sys
import csv
import os.path

strPrefix = "" if ( len( sys.argv ) <= 1 ) else sys.argv[1]
strSuffix = "" if ( len( sys.argv ) <= 2 ) else sys.argv[2]

astrHeaders = astrIDs = []
aastrData = []
for astrLine in csv.reader( sys.stdin, csv.excel_tab ):
	strID, astrData = astrLine[0], astrLine[1:]
	if astrHeaders:
		astrIDs.append( strID )
		aastrData.append( astrData )
	else:
		astrHeaders = astrData

for iCol, strCol in enumerate( astrHeaders ):
	with open( strPrefix + strCol + strSuffix, "w" ) as ostm:
		csvw = csv.writer( ostm, csv.excel_tab )
		csvw.writerow( ("GID", "Abundance") )
		for iRow, strRow in enumerate( astrIDs ):
			csvw.writerow( (strRow, aastrData[iRow][iCol]) )
