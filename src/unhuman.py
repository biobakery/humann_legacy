#!/usr/bin/env python

import csv
import subprocess
import sys

c_setstrSpecial	= set(("STSite", "Percent of Human Reads"))
c_strName		= "NAME"
c_setstrSkip	= set((">", "+"))
c_strDone		= "DONE"

if len( sys.argv ) < 3:
	raise Exception( "Usage: unhuman.py <unhuman.R> <metadata.txt> [status.txt] < <data.pcl>" )
strR, strMetadata = sys.argv[1:3]
strStatus = sys.argv[3] if ( len( sys.argv ) > 3 ) else None

for astrLine in csv.reader( open( strMetadata ), csv.excel_tab ):
	setstrMetadata = set(astrLine)
	break
setstrMetadata -= c_setstrSpecial

aastrLines = [a for a in csv.reader( sys.stdin, csv.excel_tab )]
fProc = True
for strSpecial in c_setstrSpecial:
	if strSpecial not in [a[0] for a in aastrLines]:
		fProc = False
		break
if fProc:
	proc = subprocess.Popen( ["R", "--vanilla", "-q", "-f", strR], stdin = subprocess.PIPE, stdout = subprocess.PIPE )
	for iCol2Row in range( len( aastrLines[0] ) ):
		if aastrLines[0][iCol2Row] == c_strName:
			continue
		astrLine = []
		for iRow2Col in range( len( aastrLines ) ):
			if aastrLines[iRow2Col][0] not in setstrMetadata:
				astrLine.append( aastrLines[iRow2Col][iCol2Row] )
		proc.stdin.write( "%s\n" % "\t".join( astrLine ) )
	strTable = proc.communicate( )[0]

	fileStatus = open( strStatus, "w" ) if strStatus else None	
	fDone = False
	aastrOut = []
	for strLine in strTable.split( "\n" ):
		if ( not strLine ) or ( strLine[0] in c_setstrSkip ):
			continue
		if not fDone:
			if strLine.find( c_strDone ) >= 0:
				fDone = True
			elif fileStatus:
				fileStatus.write( "%s\n" % strLine )
			continue
		aastrOut.append( strLine.strip( ).split( "\t" ) )
	
	for iRow2Col in range( 1, len( aastrLines ) ):
		if aastrLines[iRow2Col][0] in ( setstrMetadata | c_setstrSpecial ):
			continue
		for iCol2Row in range( 2, len( aastrLines[iRow2Col] ) ):
			aastrLines[iRow2Col][iCol2Row] = aastrOut[iCol2Row - 1][iRow2Col - len( setstrMetadata ) + 1]
for astrLine in aastrLines:
	print( "\t".join( astrLine ) )
