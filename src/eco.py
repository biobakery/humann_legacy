#!/usr/bin/env python

"""
Description: Calculates ecological statistics on an input function
Point in the pipeline: Finishing steps.
Program called before: filter.py or normalize.py.
Program called after: metadata.py.
"""

import csv
import math
import sys

def funcInvSimp( adData ):
	""" Calculates the inverse Simpson (diversity) index. """
	
	return ( 1.0 / ( sum( ( d * d ) for d in adData ) or 1 ) )

def funcShan( adData ):
	""" Calculates the Shannon richness index. """

	return -sum( ( ( d * math.log( d ) ) if d else 0 ) for d in adData )

def funcPielou( adData ):
	""" Calculates Pielou's evenness index. """

	adData = list(adData)
	return ( ( funcShan( adData ) / math.log( len( adData ) ) ) if adData else 0 )

def funcRichness( adData ):
	""" Calculates richness. """
	return sum( adData )

# Creates table with richness/evenness values from above.

astrColumns = [] # Holds all the header information for the columns (either ID, Organism Name, Data) or just (ID, Data), depending on whether organism specificity is turned on.
astrRows = [] # Holds all of the rows of the data.
aadData = [] # Holds all of the data (without IDs or Organism names, just numbers).
fOrg = False
for astrLine in csv.reader( sys.stdin, csv.excel_tab ): # Open the stdin file, assume it is in excel tab-delimited format.
	if ( astrLine[1] == "Organism" ) | fOrg: # If the second column reads "Organism", or the fOrg flag returns true,
		strID, strOrg, astrData = astrLine[0], astrLine[1], astrLine[2:] # Then the ID (strID) is in the first column, organism name (strOrg) is in the second column, and the rest of the data (astrData) is in the remaining columns.
	else:
		strID, astrData = astrLine[0], astrLine[1:] # If not an organism-specified file, then the ID (strID) is in the first column and the data (astrData) is in all of the remaining columns.
	if astrColumns: # If astrColumns already exists,
		if fOrg: # If the fOrg flag is true,
			astrRows.append( "\t".join( ( strID, strOrg ) ) ) # Append the ID in the first column and the organism name in the second column of a new line of astrRows (columns separated by tabs)
		else: # If astrColumns already exists but fOrgs flag is false,
			astrRows.append( strID ) # Append the ID to a new line of astrRows.
		aadData.append( [float(s) for s in astrData] ) # Append the float value of all data in astrData to aadData.
	else: # If astrColumns has not been created yet,
		fOrg = astrLine[1] == "Organism" # Set the fOrg flag to true if the second column of this (first) line is "Organism".
		if fOrg: # If the file is organism-specific,
			astrColumns = ["\t".join( ( astrLine[0], astrLine[1] ) )] + astrLine[2:] # Then set astrColumns to the tab-joined columns of ID in the first column, organism name in the second column, and the rest of the data in the remaining columns.
		else:
			astrColumns = astrLine # Otherwise, just load the entire line in astrColumns.

print( "\t".join( astrColumns ) ) # Print the prepared row astrColumns separated by tabs to stdout.
for strID, funcID in (
	("InverseSimpson",	funcInvSimp),
	("Shannon",			funcShan),
	("Pielou",			funcPielou),
	("Richness",		funcRichness),
	):
	print( "\t".join( [strID] + [( "%g" % funcID( aadData[i][j] for i in range( len( astrRows ) ) ) ) # Print to stdout the following separated by tabs: strID, (each element in aadData in turn).
		for j in range( len( astrColumns ) - 1 )] ) )
for iRow in range( len( astrRows ) ):
	print( "\t".join( [astrRows[iRow]] + [( "%g" % aadData[iRow][i] ) for i in range( len( aadData[iRow] ) )] ) ) # print to stdout: each row in astrRows + the data in aadData corresponding to that row.
