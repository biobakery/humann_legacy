#!/usr/bin/env python

import csv
import re
import sys

if len( sys.argv ) != 2:
	raise Exception( "Usage: pathways2grings.py <graphlan> < <04b.txt>" )
strTree = sys.argv[1]

hashTree = {}
for strLine in open( strTree, "rU" ):
	strLine = strLine.rstrip( )
	hashTree[strLine.split( "_" )[-1]] = strLine

astrHeaders = None
fOrg = fHit = False
astrIDs = []
aadData = []
for astrLine in csv.reader( sys.stdin, csv.excel_tab ):
	if not astrHeaders:
		fOrg = ( astrLine[2] == "Organism" )
	strID, astrData = astrLine[0], astrLine[( 3 if fOrg else 2 ):]
	if not astrHeaders:
		astrHeaders = astrData
		continue
	strHit = hashTree.get( strID )
	if not fHit:
		fHit = strHit
	if fHit:
		astrIDs.append( strHit )
		aadData.append( [float(s) for s in astrData] )
dMax = max( d for a in aadData for d in a )

csvw = csv.writer( sys.stdout, csv.excel_tab )
for iCol, strCol in enumerate( astrHeaders ):
	csvw.writerow( ("ring_label_color", ( iCol + 1 ), "#FFFFFF") )
	csvw.writerow( ("ring_label", ( iCol + 1 ), re.sub( r'-.+', "", strCol )) )
for iRow, strRow in enumerate( astrIDs ):
	for iCol, d in enumerate( aadData[iRow] ):
		csvw.writerow( (strRow, "ring_color", ( iCol + 1 ),
			( "#%02X0000" % ( ( d / dMax ) * 255 ) )) )
