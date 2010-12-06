#!/usr/bin/env python

import re
import sys

astrIDs = []
asetMaps = []
setMap = fGenes = strSpecies = None
for strLine in sys.stdin:
	mtch = re.search( '^ENTRY\s+(\S+)', strLine )
	if mtch:
		astrIDs.append( mtch.group( 1 ) )
		setMap = set()
		asetMaps.append( setMap )
		continue
	mtch = re.search( '^GENES(.+)', strLine )
	if mtch:
		strLine = mtch.group( 1 )
		fGenes = True
	mtch = re.search( '^\S', strLine )
	if ( not fGenes ) or mtch:
		fGenes = False
		continue

	strLine = strLine.strip( )
	mtch = re.search( '^(\S{3}):\s+(.+)', strLine )
	if mtch:
		strSpecies, strLine = mtch.groups( )
	for strToken in re.split( '\s+', strLine ):
		mtch = re.search( '^(\S+)\((.+)\)$', strToken )
		astrGenes = [mtch.group( 1 ) if mtch else strToken]
		for strGene in astrGenes:
			setMap.add( strSpecies + "#" + strGene.upper( ) )

for i in range( len( astrIDs ) ):
	if asetMaps[i]:
		print( "\t".join( [astrIDs[i]] + list(asetMaps[i]) ) )
