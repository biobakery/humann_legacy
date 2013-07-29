#!/usr/bin/env python

"""
Description: Replaces any blank spaces in stdin  with the string "0".
Point in the pipeline: Finishing steps.
Program called before: humann.py.
Program called after: filter.py.
"""
import sys

for strLine in sys.stdin: # For each line (strLine) in stdin:
	astrLine = strLine.split( "\t" ) # Split the line by tabs into columns.
	for i in range( len( astrLine ) ): # For each collumn in the current line:
		astrLine[i] = astrLine[i].strip( ) # Remove any extra whitespace.
		if not astrLine[i]: 
			astrLine[i] = "0" # Replace any values of 'None' with a string "0" instead.
	print( "\t".join( astrLine ) ) # Print the columns of the current line, joined by tabs.
