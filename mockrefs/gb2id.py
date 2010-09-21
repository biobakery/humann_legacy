#!/usr/bin/env python

import re
import sys

strLocus = None
for strLine in sys.stdin:
	pMatch = re.search( '(?:(?:locus_tag)|(?:gene))\s*=\s*\"([^"]+)\"',
		strLine )
	if pMatch:
		strLocus = pMatch.group( 1 )
		continue
	pMatch = re.search( 'protein_id\s*=\s*\"([^"]+)\"', strLine )
	if pMatch:
		print( "\t".join( (pMatch.group( 1 ), strLocus) ) )
