#!/usr/bin/env python

import re
import sys

astrPaths = sys.argv[1:]

for strPaths in astrPaths:
	mtch = re.search( '(\S{3})_pathway\.list', strPaths )
	if not mtch:
		raise Exception( "Illegal pathway: " + strPaths )
	strOrg = mtch.group( 1 )
	setstrOrg = set()
	for strLine in open( strPaths ):
		strGene, strPath = strLine.strip( ).split( "\t" )
		setstrOrg.add( "ko" + strPath[8:] )
	if setstrOrg:
		print( "\t".join( [strOrg] + [( strCur + "#1" ) for strCur in setstrOrg] ) )
