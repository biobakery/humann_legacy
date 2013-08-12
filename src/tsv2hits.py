#!/usr/bin/env python

import sys
import csv
import os.path

astrHeaders = astrIDs = []
aadData = []
for strLine in sys.stdin:
	astrLine = strLine.rstrip( ).split( "\t" ) # Split each line of the document by tabs, and then strip it of extra whitespace.
	strID, astrData = astrLine[0], astrLine[1:] # First column is the ID (strID), all subsequent columns are the data (strData).
	if astrHeaders: # If the header row has aready been defined and thus this is a subsequent row:
		astrIDs.append( strID ) # Apend this row's ID to the array of IDs.
		aadData.append( [float(s) for s in astrData] ) # Apend the data in this row to the array holding the data.
	else:
		astrHeaders = astrData # If this is the header row and thus astrHeaders has not been previously defined, define it to be this row's data.

for iCol, strCol in enumerate( astrHeaders ): # iCol is the index of the column, strCol is the value in that column.

	ostm = open( join( c_strDirOutput, strCol "_01-keg" + c_strSuffixOutput ), "w" ) # maybe need to say 'path.join' instead of just .join.
	# Replace '-keg' with c_strDatabaseLabel (which I will need to define)
	# REMOVE HARDCODING ?
	# QUESTION: Can I grab arguements from the SConstruct file that is calling this one? If so I could construct the only remaining hardcoding here, "_01-keg", from those values. Otherwise I don't think I can.
	ostm.write( "GID\tAbundance\n" ) # Make GID, Abundance, etc global constants.
	# REMOVE HARDCODING ? Do I need to further reduce the hardcoding here, or is it acceptable as it is?
	for iRow, strRow in enumerate( astrIDs ): # iRow is the index of the list of IDs, strRow is the list of IDs itself.
		ostm.write( "%s\t%g\n" % (strID, aadData[iRow][iCol]) ) # Write to the output file the ID in the first column (strID), and then the data value in the second column