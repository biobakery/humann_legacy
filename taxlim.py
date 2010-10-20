#!/usr/bin/env python

import sys

c_dIQRs		= 0
c_fMedian	= False

if len( sys.argv ) < 2:
	raise Exception( "Usage: taxlim.py <taxpc> [iqrs=" + str(c_dIQRs) + "] [median=" +
		str(c_fMedian) + "] < <pathways.txt>" )
strTaxPC = sys.argv[1]
dIQRs = c_dIQRs if ( len( sys.argv ) <= 2 ) else float(sys.argv[2])
fMedian = c_fMedian if ( len( sys.argv ) <= 3 ) else ( int(sys.argv[3]) != 0 )

hashhashTaxa = {}
for strLine in open( strTaxPC ):
	astrLine = strLine.strip( ).split( "\t" )
	hashhashTaxa[astrLine[0]] = hashTaxon = {}
	for strToken in astrLine[1:]:
		strPath, strScore = strToken.split( "#" )
		hashTaxon[strPath] = float(strScore)

hashhashKOs = {}
hashOrgs = {}
for strLine in sys.stdin:
	astrLine = strLine.strip( ).split( "\t" )
	if astrLine[0] == "GID":
		continue
	if astrLine[0] == "#":
		hashOrgs[astrLine[1]] = float(astrLine[2])
		continue
	hashhashKOs.setdefault( astrLine[0], {} )[astrLine[1]] = float(astrLine[2])

hashTaxlim = {}
for strOrg, dOrg in hashOrgs.items( ):
	for strPath, dPath in hashhashTaxa.get( strOrg, {} ).items( ):
		hashTaxlim[strPath] = ( dOrg * dPath ) + hashTaxlim.get( strPath, 0 )
adTaxlim = sorted( hashTaxlim.values( ) )
dLF = -1
if len( adTaxlim ) > 2:
	if fMedian:
		d25, d50, d75 = (adTaxlim[int(round( 0.25 * i * len( adTaxlim ) ))] for i in (1, 2, 3))
		dIQR = d75 - d25
		dLF = d50 - ( dIQRs * dIQR )
	else:
		dAve = dStd = 0
		for d in adTaxlim:
			dAve += d
			dStd += d * d
		dAve /= len( adTaxlim )
		dStd = ( ( dStd / ( len( adTaxlim ) - 1 ) ) - ( dAve * dAve ) )**0.5
		dLF = dAve + ( dIQRs * dStd )

def funcCmp( aOne, aTwo ):
	
	i = cmp( aTwo[1], aOne[1] )
	return ( i if i else cmp( hashTaxlim.get( aTwo[0], 0 ), hashTaxlim.get( aOne[0], 0 ) ) )

print( "GID	Pathway	Abundance" )
for strKO, hashPaths in hashhashKOs.items( ):
	aaPaths = sorted( hashPaths.items( ), cmp = funcCmp )
	while len( aaPaths ) > 1:
		strPath, dPath = aaPaths[-1]
		if hashTaxlim.get( strPath, 0 ) > dLF:
			break
#		sys.stderr.write( "%s\n" % [strKO, strPath, dPath] )
		aaPaths.pop( )
	for aPath in aaPaths:
		print( "\t".join( [strKO] + [str(pCur) for pCur in aPath] ) )
