#!/usr/bin/env python

"""
Description: Takes an input file from the command line, and writes all of stdin input to that file.
"""

import sys

if len( sys.argv ) != 2:
	raise Exception( "Usage: output.py <file>" )
strOut = sys.argv[1] # strOut is the file being considered.

strLine = sys.stdin.readline( ) # strLine is a line from stdin.
if not strLine:
	sys.exit( 1 ) # If there is no input from stdin, then exit with error status "1".
fileOut = open( strOut, "w" ) # Open the file passed in on the command line, assign it the pointer fileOut.
fileOut.write( strLine ) # Add the line from stdin to the file from the command line.
for strLine in sys.stdin:
	fileOut.write( strLine ) # Add all the lines from stdin to the file from the command line.
fileOut.close( ) # Close the opened file from the command line.
