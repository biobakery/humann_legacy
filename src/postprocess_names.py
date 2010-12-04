#!/usr/bin/env python

import sys

if len( sys.argv ) != 2:
	raise Exception( "Usage: postprocess_names.py <named.pcl> < <unnamed.pcl>" ); end
strNamed = sys.argv[1]

hashNames = {}
for strLine in open( strNamed ):
	astrLine = strLine.rstrip( "\n\r" ).split( "\t" )
	if ( len( astrLine ) > 1 ) and astrLine[1]:
		hashNames[astrLine[0]] = astrLine[1]

fFirst = True
for strLine in sys.stdin:
	astrLine = strLine.rstrip( "\n\r" ).split( "\t" )
	astrLine.insert( 1, "" )
	if fFirst:
		fFirst = False
		astrLine[1] = "NAME"
	else:
		strGloss = hashNames.get( astrLine[0] )
		astrLine[1] = astrLine[0] + ( ( ": " + strGloss ) if strGloss else "" )
	print( "\t".join( astrLine ) )
