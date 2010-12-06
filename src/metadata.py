#!/usr/bin/env python

import re
import sys

c_strBlank	= " "

if len( sys.argv ) != 2:
	raise Exception( "Usage: metadata.py <metadata.txt> < <data.pcl>" )
strMetadata = sys.argv[1]

astrMetadata = None
hashMetadata = {}
for strLine in open( strMetadata ):
	astrLine = strLine.strip( ).split( "\t" )
	strID, astrData = astrLine[0], astrLine[1:]
	if astrMetadata:
		if len( astrData ) < len( astrMetadata ):
			astrData += [c_strBlank] * ( len( astrMetadata ) - len( astrData ) )
		hashMetadata[strID] = astrData
	else:
		astrMetadata = astrData

fFirst = True
for strLine in sys.stdin:
	sys.stdout.write( strLine )
	if not fFirst:
		continue

	fFirst = False
	astrLine = strLine.strip( ).split( "\t" )
	astrIDs = []
	for strIn in astrLine[1:]:
		strOut = None
		for strCur, astrCur in hashMetadata.items( ):
			if strIn.find( strCur ) >= 0:
				strOut = strCur
				break
		astrIDs.append( strOut )
	for i in range( len( astrMetadata ) ):
		print( "\t".join( [astrMetadata[i]] + map( lambda s: hashMetadata.get( s, [c_strBlank] * ( i + 1 ) )[i], astrIDs ) ) )
