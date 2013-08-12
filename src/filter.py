#!/usr/bin/env python

"""
Description: 
Example call: src/filter.py data/pathwayc data/modulep
Point in the pipeline: Finishing steps.
Program called before: zero.py.
Program called after: eco.py or normalize.py.
"""

import pathway # Part of HUMAnN, see src/pathway.py.
import re
import sys

c_iSize	= 4

astrPaths = sys.argv[1:] # Grabs all files passed in with the commandline (presumably data/pathwayc and data/modulep).

hashPaths = {} # Dict holding all of pathways.
for strPaths in astrPaths: # For each file (strPaths) in the commandline input:
	for pPathway in pathway.open( open( strPaths ) ): # The pathway.open( ) function opens a file (data/pathwayc or data/modulec usually) and returns an array of pointers to CPathway objects, one CPathway object for every line in the file.
		hashPaths[pPathway.id( )] = min( pPathway.size( ), hashPaths.get( pPathway.id( ), pPathway.size( ) ) ) # Construct a dict in mapping pathway id to the size of that pathway.


fFirst = True # Flag denoting this is the first 
for strLine in sys.stdin: 
	mtch = re.search( '^([^\t]*)\t', strLine )
	if ( not fFirst ) and mtch:
		iSize = hashPaths.get( mtch.group( 1 ), c_iSize )
		if iSize < c_iSize:
			continue
	fFirst = False
	sys.stdout.write( strLine )
