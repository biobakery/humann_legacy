#!/usr/bin/env python

import re
import sys

astrTables = sys.argv[1:]
if len( astrTables ) > 1:
	astrTables = [astrTables[0]] + sorted( astrTables[1:] )

aastrHeaders = []
hashResults = {}
fOrg = False
for iTable in range( len( astrTables ) ):
	fFirst = True
	for strLine in open( astrTables[iTable] ):
		astrLine = [strToken.strip( ) for strToken in strLine.split( "\t" )]
		if ( astrLine[1] == "Organism" ) | fOrg:
			astrData = astrLine[2:]
		else:
			astrData = astrLine[1:]
		if fFirst:
			fFirst = False
			fData = False
			try:
				[float(s) for s in astrData]
				fData = True
			except ValueError:
				pass
			if fData:
				aastrHeaders.append( [( "C%d" % ( i + 1 ) ) for i in xrange( len( astrData ) )] )
			else:
				fOrg = ( astrLine[1] == "Organism" )
				aastrHeaders.append( astrData )
				continue
		if astrLine[0] == "#":
			continue
		if fOrg:
			aastrRow = hashResults.setdefault( "\t".join( ( astrLine[0], astrLine[1] ) ), [] )
		else:
			aastrRow = hashResults.setdefault( astrLine[0], [] )
		if len( aastrRow ) <= iTable:
			aastrRow += [None] * ( 1 + iTable - len( aastrRow ) )
		aastrRow[iTable] = astrData

sys.stdout.write( "ID" )
if fOrg:
	sys.stdout.write( "	Organism" )
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
