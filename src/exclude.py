#!/usr/bin/env python

import re
import sys

if len( sys.argv ) != 2:
	raise Exception( "Usage: exclude.py <exclude.txt> < <data.pcl>" )
strExclude = sys.argv[1]

setExclude = set()
for strLine in open( strExclude ):
	setExclude.add( strLine.strip( ) )

afInclude = None
for strLine in sys.stdin:
	astrLine = strLine.strip( ).split( "\t" )
	if not afInclude:
		afInclude = [True] * len( astrLine )
		for i in range( len( astrLine ) ):
			mtch = re.search( r'^([^ _-]+)', astrLine[i] )
			if mtch and ( mtch.group( 1 ) in setExclude ):
				afInclude[i] = False
	print( "\t".join( astrLine[i] for i in filter( lambda i: afInclude[i], range( len( astrLine ) ) ) ) )
