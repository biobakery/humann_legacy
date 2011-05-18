#!/usr/bin/env python

import sys

if len( sys.argv ) != 2:
	raise Exception( "Usage: smooth_wb.py <keggc> < <pathways.txt>" )
strKEGGC = sys.argv[1]

hashKEGGs = {}
for strLine in open( strKEGGC ):
	astrLine = strLine.strip( ).split( "\t" )
	hashKEGGs[astrLine[0]] = astrLine[1:]

setKEGGs = set()
setKOs = set()
hashhashHits = {}
for strLine in sys.stdin:
	strKO, strKEGG, strScore = strLine.strip( ).split( "\t" )
	if strKO == "GID":
		sys.stdout.write( strLine )
		continue
	setKEGGs.add( strKEGG )
	setKOs = setKOs.union( hashKEGGs.get( strKEGG, () ) )
	setKOs.add( strKO )
	hashhashHits.setdefault( strKO, {} )[strKEGG] = float(strScore)
iT = len( hashhashHits )
dN = 0
for strKO, hashKO in hashhashHits.items( ):
	dN += sum( hashKO.values( ) ) / len( hashKO )
d = dN + iT
if d:
	dN /= d

iDen = len( setKOs ) - iT
dZero = ( float(iT) / iDen ) if iDen else 0
setHits = set()
for strKO, hashKO in hashhashHits.items( ):
	for strKEGG, dScore in hashKO.items( ):
		setHits.add( "_".join( (strKO, strKEGG) ) )
		if dScore == 0:
			dScore = dZero
		print( "\t".join( (strKO, strKEGG, str(dScore * dN)) ) )
for strKEGG in setKEGGs:
	for strKO in hashKEGGs.get( strKEGG, () ):
		if "_".join( (strKO, strKEGG) ) not in setHits:
			print( "\t".join( (strKO, strKEGG, str(dZero * dN)) ) )
