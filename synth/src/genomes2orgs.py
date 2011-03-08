#!/usr/bin/env python

import math
import random
import re
import sys

if len( sys.argv ) != 2:
	raise Exception( "Usage: genomes2orgs.py <orgs> < <genome>" )
iOrgs = int(sys.argv[1])

strID = fOK = None
setTaxa = set()
for strLine in sys.stdin:
	mtch = re.search( '^NAME\s+([a-z]{3}),', strLine )
	if mtch:
		strID = mtch.group( 1 )
		fOK = False
		continue
	if re.search( '^ANNOTATION\s+manual', strLine ):
		fOK = True
	if not fOK:
		continue
	mtch = re.search( '^\s*LINEAGE\s+Bacteria', strLine )
	if mtch:
		setTaxa.add( strID )

for strTaxon in random.sample( setTaxa, min( iOrgs, len( setTaxa ) ) ):
# Lognormal random deviates
	d = math.exp( 2 * random.gauss( 0, 1 ) )
	print( "\t".join( (strTaxon, str(d)) ) )
	