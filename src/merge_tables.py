#!/usr/bin/env python

import re
import sys

astrTables = sys.argv[1:]
if len( astrTables ) > 1:
	astrTables = [astrTables[0]] + sorted( astrTables[1:] )

aastrHeaders = []
hashResults = {}
for iTable in range( len( astrTables ) ):
	fFirst = True
	for strLine in open( astrTables[iTable] ):
		astrLine = [strToken.strip( ) for strToken in strLine.split( "\t" )]
		astrData = astrLine[1:]
		if fFirst:
			fFirst = False
			aastrHeaders.append( astrData )
			continue
		if astrLine[0] == "#":
			continue
		aastrRow = hashResults.setdefault( astrLine[0], [] )
		if len( aastrRow ) <= iTable:
			aastrRow += [None] * ( 1 + iTable - len( aastrRow ) )
		aastrRow[iTable] = astrData

sys.stdout.write( "ID" )
for iTable in range( len( astrTables ) ):
	astrHeaders = [astrTables[iTable]] + aastrHeaders[iTable][1:]
	pMatch = re.search( '^(?:.*\/)?(.+)_\d+[a-z]*(-[^.]+)?', astrHeaders[0] )
	if pMatch:
		astrHeaders[0] = pMatch.group( 1 ) + ( pMatch.group( 2 ) or "" )
	pMatch = re.search( '(\d+)_alignments(\d+)', astrHeaders[0] )
	if pMatch:
		astrHeaders[0] = pMatch.group( 1 ) + " " + pMatch.group( 2 )
	pMatch = re.search( '-\d+-(\d+)', astrHeaders[0] )
	if pMatch:
		astrHeaders[0] = pMatch.group( 1 )
	sys.stdout.write( "\t" + "\t".join( astrHeaders ) )
print( "" )

for strID, aastrData in hashResults.items( ):
	sys.stdout.write( strID )
	for iDatum in range( len( aastrHeaders ) ):
		astrData = aastrData[iDatum] if ( iDatum < len( aastrData ) ) else \
			None
		strData = "\t".join( astrData ) if astrData else \
			( "\t" * ( len( aastrHeaders[iDatum] ) - 1 ) )
		sys.stdout.write( "\t" + strData )
	print( "" )
