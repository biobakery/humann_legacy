#!/usr/bin/env python

import pathway
import sys

c_fMedian	= True

if len( sys.argv ) < 2:
	raise Exception( "Usage: pathcov.py <keggc> [modulep] [median=" + str(c_fMedian) + "] < <pathways.txt>" )
strKEGGC = sys.argv[1]
strModuleP = None if ( len( sys.argv ) <= 2 ) else sys.argv[2]
fMedian = c_fMedian if ( len( sys.argv ) <= 3 ) else ( int(sys.argv[3]) != 0 )

hashKEGGs = {}
for strLine in open( strKEGGC ):
	astrLine = strLine.strip( ).split( "\t" )
	hashKEGGs[astrLine[0]] = astrLine[1:]

hashModules = {}
if strModuleP:
	for pPathway in pathway.open( open( strModuleP ) ):
		hashModules[pPathway.id( )] = pPathway

dAve = iAve = 0
adScores = []
hashhashScores = {}
for strLine in sys.stdin:
	strLine = strLine.strip( )
	astrLine = strLine.split( "\t" )
	if astrLine[0] == "GID":
		fOrg = len( astrLine ) > 3
		continue
	dAb = float( astrLine[3] ) if fOrg else float( astrLine[2] )
	hashhashScores.setdefault( astrLine[1] if fOrg else None, {} ).setdefault( astrLine[2] if fOrg else astrLine[1], {} )[astrLine[0]] = dAb
	adScores.append( dAb )
	dAve += dAb
	iAve += 1
if iAve:
	dAve /= iAve
adScores.sort( )
if adScores:
	dMed = adScores[len( adScores ) / 2] if fMedian else ( sum( adScores ) / len( adScores ) )
sys.stdout.write( "PID	" )
if fOrg:
	sys.stdout.write( "Organism	" )
print( "Coverage" )
for strOrg, hashScores in hashhashScores.items( ):
	for strKEGG, hashKOs in hashScores.items( ):
		astrKOs = hashKEGGs.get( strKEGG )
		if astrKOs:
			for strKO in astrKOs:
				hashKOs.setdefault( strKO, 0 )
		if not ( strKEGG and hashKOs ):
			continue
		pPathway = hashModules.get( strKEGG )
		if pPathway:
			dCov = pPathway.coverage( hashKOs, dMed )
		else:
			iHits = 0
			for strKO, dAb in hashKOs.items( ):
				if dAb > dMed:
					iHits += 1
			dCov = float(iHits) / len( hashKOs )
		if fOrg:
			print( "\t".join( (strKEGG, strOrg, str(dCov)) ) )
		else:
			print( "\t".join( (strKEGG, str(dCov)) ) )
