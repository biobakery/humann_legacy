#!/usr/bin/env python

import csv
import sys
import re

if len( sys.argv ) < 2:
	raise Exception( "Usage: pathways2graphlan.py <kegg-graphlan> < <input.txt>" )
strKEGGG = sys.argv[1]

iLine = 4
iCLine = 0

aPaths = []
hashOrgs = {}
fOrg = False
fFirst = True
for astrLine in csv.reader( sys.stdin, csv.excel_tab ):
	if fFirst:
		fFirst = False
		fOrg = ( astrLine[2] == "Organism" )
	else:
		if fOrg:
			aPaths.append( (astrLine[0], astrLine[2]) )
		else:
			aPaths.append( astrLine[0] )

hashMeta = {}
pattern = re.compile('[\W_]+')
fClass = False
for strLine in open( strKEGGG, "rU" ):
	strLine = strLine.rstrip( )
	hashMeta[strLine.split( "_" )[-1]] = strLine

fHit = False
for pPath in aPaths:
	strKEGG, strOrg = pPath if fOrg else (pPath, "")
	strMeta = hashMeta.get( strKEGG )
#	sys.stderr.write( "%s\n" % [strKEGG, strOrg, strMeta] )
	if strMeta:
		fHit = True
	if fHit:
		print( hashMeta.get( strKEGG, strKEGG ) + ( ( "_" + strOrg ) if fOrg else "" ) )
