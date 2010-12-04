#!/usr/bin/env python

import re
import sys

def pt( strID, strSeq ):
	
	if strID:
		print( "\t".join( (strID, str(len( strSeq ))) ) )

strID = strSeq = None
for strLine in sys.stdin:
	mtch = re.search( '^>(\S+)', strLine )
	if mtch:
		pt( strID, strSeq )
		strID = mtch.group( 1 )
		strSeq = ""
		continue
	strSeq += strLine.strip( )
pt( strID, strSeq )
