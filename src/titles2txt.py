#!/usr/bin/env python

import re
import sys

strModule = sys.argv[1] if ( len( sys.argv ) > 1 ) else None

if strModule:
	strID = None
	for strLine in open( strModule ):
		mtch = re.search( '^ENTRY\s+(M\d+)', strLine )
		if mtch:
			strID = mtch.group( 1 )
			continue
		mtch = re.search( '^NAME\s+(.+)$', strLine )
		if mtch:
			print( "\t".join( (strID, mtch.group( 1 )) ) )
			continue

for strLine in sys.stdin:
	sys.stdout.write( "ko" + strLine )
