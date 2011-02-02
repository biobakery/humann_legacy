#!/usr/bin/env python

import re
import sys

if len( sys.argv ) != 1:
	raise Exception( "Usage: metacyc2mcc.py < <reactions.dat>" )

strID = strEC = astrGenes = None
for strLine in sys.stdin:
	mtch = re.search( r'^UNIQUE-ID\s+-\s+(\S+)', strLine )
	if mtch:
		strID = mtch.group( 1 )
		strEC = ""
		astrGenes = []
		continue
	mtch = re.search( r'^DBLINKS\s+-\s+\(\s*UNIPROT\s+"([^"]+)"', strLine )
	if mtch:
		astrGenes.append( mtch.group( 1 ) )
		continue
	mtch = re.search( r'^EC-NUMBER\s+\-\s+(\S+)', strLine )
	if mtch:
		strEC = mtch.group( 1 )
		continue
	if strLine.startswith( "//" ) and astrGenes:
		print( "\t".join( [strID, strEC] + astrGenes ) )
		continue
