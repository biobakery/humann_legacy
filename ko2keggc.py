#!/usr/bin/env python

import re
import sys

strKO = None
hashKEGGs = {}
for strLine in sys.stdin:
	mtch = re.search( '^ENTRY\s+(K\d+)', strLine )
	if mtch:
		strKO = mtch.group( 1 )
		continue
#	mtch = re.search( '(?:(?:PATH)|(?:BR)):(ko\d+)', strLine )
	mtch = re.search( 'PATH:(ko\d+)', strLine )
	if mtch:
		hashKEGGs.setdefault( mtch.group( 1 ), set() ).add( strKO )

for strKEGG, setKOs in hashKEGGs.items( ):
	print( "\t".join( [strKEGG] + list(setKOs) ) )
