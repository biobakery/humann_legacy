#!/usr/bin/env python

import re
import sys

c_iID, c_iCOG	= 5, 7

def lookup( strIn, hashMap ):

	for strCur in (strIn, strIn.replace( "_", "" )):
		strRet = hashID2GB.get( strCur )
		if strRet:
			return strRet

	return None

if len( sys.argv ) != 2:
	raise Exception( "Usage: gb2cg.py <gb2id.txt> < <data.ptt>" )
strGB2ID = sys.argv[1]

hashID2GB = {}
for strLine in open( strGB2ID ):
	strGB, strID = strLine.strip( ).split( "\t" )
	hashID2GB[strID] = hashID2GB[strID.replace( "_", "" )] = strGB

strLocus = None
for strLine in sys.stdin:
	astrLine = strLine.strip( ).split( "\t" )
	if len( astrLine ) <= max( c_iID, c_iCOG ):
		continue
	strID, strCOG = astrLine[c_iID], astrLine[c_iCOG]
	pMatch = re.search( '(COG\d+)', strCOG )
	if not pMatch:
		continue
	strCOG = pMatch.group( 1 )
	strGB = lookup( strID, hashID2GB )
	if strGB:
		print( "\t".join( (strGB, strCOG) ) )
