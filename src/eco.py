#!/usr/bin/env python

import csv
import math
import sys

# Calculates the inverse Simpson index

def funcInvSimp( adData ):
	
	return ( 1.0 / ( sum( ( d * d ) for d in adData ) or 1 ) )

# Calculates the Shannon index

def funcShan( adData ):
	
	return -sum( ( ( d * math.log( d ) ) if d else 0 ) for d in adData )

# Calculates Pielou's evenness index

def funcPielou( adData ):
	
	adData = list(adData)
	return ( ( funcShan( adData ) / math.log( len( adData ) ) ) if adData else 0 )

# Calculates richness

def funcRichness( adData ):
	
	return sum( adData )

# Creates table with richness/evenness values from above

astrColumns = []
astrRows = []
aadData = []
fOrg = False
for astrLine in csv.reader( sys.stdin, csv.excel_tab ):
	if ( astrLine[1] == "Organism" ) | fOrg:
		strID, strOrg, astrData = astrLine[0], astrLine[1], astrLine[2:]
	else:
		strID, astrData = astrLine[0], astrLine[1:]
	if astrColumns:
		if fOrg:
			astrRows.append( "\t".join( ( strID, strOrg ) ) )
		else:
			astrRows.append( strID )
		aadData.append( [float(s) for s in astrData] )
	else:
		fOrg = astrLine[1] == "Organism"
		if fOrg:
			astrColumns = ["\t".join( ( astrLine[0], astrLine[1] ) )] + astrLine[2:]
		else:
			astrColumns = astrLine

print( "\t".join( astrColumns ) )
for strID, funcID in (
	("InverseSimpson",	funcInvSimp),
	("Shannon",			funcShan),
	("Pielou",			funcPielou),
	("Richness",		funcRichness),
	):
	print( "\t".join( [strID] + [( "%g" % funcID( aadData[i][j] for i in range( len( astrRows ) ) ) )
		for j in range( len( astrColumns ) - 1 )] ) )
for iRow in range( len( astrRows ) ):
	print( "\t".join( [astrRows[iRow]] + [( "%g" % aadData[iRow][i] ) for i in range( len( aadData[iRow] ) )] ) )
