#!/usr/bin/env python

import re
import sys

if len( sys.argv ) != 1:
	raise Exception( "Usage: metacyc2mcc.py < <uniprot-seq-ids.txt>" )

strID = astrGenes = None
for strLine in sys.stdin:
	mtch = re.search( '\(+(\S+)(.+)', strLine )
	if mtch:
		strID = re.sub( '\|$', "", re.sub( '^\|', "", mtch.group( 1 ) ) )
		strLine = mtch.group( 2 )
		astrGenes = []
	if astrGenes == None:
		continue
	astrGenes += [strCur.replace( "\"", "" ) for strCur in strLine.strip( ).split( " " )]
	mtch = re.search( '\)\s*$', strLine )
	if mtch:
		print( "\t".join( [strID] + astrGenes ) )
