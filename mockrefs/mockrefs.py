#!/usr/bin/env python

import sys

if len( sys.argv ) < 2:
	raise Exception( "Usage: mockrefs.py <data.gb2cg> < <cogc>" )
astrGB2CGs = sys.argv[1:]

hashCOG2KOs = {}
for strLine in sys.stdin:
	astrLine = strLine.strip( ).split( "\t" )
	strKO, astrCOGs = astrLine[0], astrLine[1:]
	for strCOG in astrCOGs:
		hashCOG2KOs.setdefault( strCOG, [] ).append( strKO )

for strGB2CG in astrGB2CGs:
	for strLine in open( strGB2CG ):
		strGB, strCOG = strLine.strip( ).split( "\t" )
		astrKOs = hashCOG2KOs.get( strCOG )
		if astrKOs:
			print( "\t".join( [strGB] + astrKOs ) )
		else:
			sys.stderr.write( "%s\n" % strCOG )