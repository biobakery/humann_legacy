#!/usr/bin/env python

"""
Description: Pulls metadata from an input file, collects and prints it to the next program in the finishing steps programs.
Point in the pipeline: Finishing steps.
Program called before: eco.py.
"""

import re
import sys

c_strBlank	= " "

if len( sys.argv ) != 2:
	raise Exception( "Usage: metadata.py <metadata.txt> <data.pcl>" )
strMetadata = sys.argv[1] # import metadata file (first commandline arguement) as strMetadata.

astrMetadata = None 
hashMetadata = {}
for strLine in open( strMetadata ): # Loop through each line of the metadata file.
	astrLine = strLine.strip( ).split( "\t" ) # Split each line by tabs.
	strID, astrData = astrLine[0], astrLine[1:] # The first column is the ID (strID), all subsequent columns are the data (astrData)
	if astrMetadata: # If there is already data in astrMetadata:
		if len( astrData ) < len( astrMetadata ): # If there are fewer entries in the current line of data than in astrMetadata:
			astrData += [c_strBlank] * ( len( astrMetadata ) - len( astrData ) ) # Then append blank spots to the current line of data until it is the same size as astrMetadata.
		hashMetadata[strID] = astrData # Load the metadata for the current line (astrData) into the hashMetadata dict, with the line key (strID) as the ID.
	else:
		astrMetadata = astrData  # If no data in astrMetadata yet, load astrData into astrMetadata.

fFirst = True # Flag denoting if this is the first line in the input file.
for strLine in sys.stdin: # Loop through the lines in the input file.
	sys.stdout.write( strLine ) # Write each line to stdOut
	if not fFirst: # If this is any line besides the first, go on to the next line.
		continue

	fFirst = False # If this was the first line, set fFirst flag to false as the first line is now past.
	astrLine = strLine.strip( ).split( "\t" ) # Split this line along tabs.
	astrIDs = []
	for strIn in astrLine[1:]: # Loop through each column after thte first of this line.
		strOut = None 
		for strCur, astrCur in hashMetadata.items( ): # strCur is each ID, astrCur is an array of each column of metadata.
			if strIn.find( strCur ) >= 0: # If the patient ID is found in the current line of the file,
				strOut = strCur # Then set strOut equal to strCur.
				break
		astrIDs.append( strOut ) # Append strOut (either a patient ID or nothing) to the list astrIDs.
	for i in range( len( astrMetadata ) ): # Loop through everything in astrMetadata.
		print( "\t".join( [astrMetadata[i]] + map( lambda s: hashMetadata.get( s, [c_strBlank] * ( i + 1 ) )[i], astrIDs ) ) ) # Print to stdout the current entry in astrMetadata, plus any entry in hashMetadata corresponding to astrIDs (if any).
