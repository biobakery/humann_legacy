#!/usr/bin/env python

import sys

fStrip = False if ( len( sys.argv ) < 2 ) else ( int(sys.argv[1]) != 0 )

for strLine in sys.stdin:
	if fStrip and strLine and ( strLine[0] == "#" ):
		continue
	sys.stdout.write( strLine )
