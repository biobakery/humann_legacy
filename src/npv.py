#!/usr/bin/env python

import matplotlib
matplotlib.use( "Agg" )
from matplotlib import pyplot
import copy
import csv
import numpy
import os
import re
import sys

c_hashGlosses	= {
	r'mock'			: "",
	r'_stg'			: "Stg.",
	r'_even'		: "Even",
	r'_hc'			: " HC",
	r'_lc'			: " LC",
	r'\.\S+$'		: "",
	r'_vs_All.*$'	: "",
}

if len( sys.argv ) < 3:
	raise Exception( "Usage: npv.py <output.png> <organisms.txt>+ <enzymes.txt>+" )
strOutput, astrFiles = sys.argv[1], sys.argv[2:]

astrOrgs = []
astrPreds = []
for strFile in astrFiles:
	( astrOrgs if ( strFile.find( "organisms_" ) >= 0 ) else astrPreds ).append( strFile )

hashhashOrgs = {}
for strOrgs in astrOrgs:
	mtch = re.search( r'organisms_(\w+)', os.path.basename( strOrgs ) )
	hashhashOrgs[mtch.group( 1 )] = hashOrgs = {}
	for astrLine in csv.reader( open( strOrgs ), csv.excel_tab ):
		if astrLine[0].strip( )[0] == "#":
			continue
		hashOrgs[astrLine[0]] = float(astrLine[1])

adNPVs = []
for strPreds in astrPreds:
	hashOrgs = None
	for strCur, hashCur in hashhashOrgs.items( ):
		if strPreds.find( "_" + strCur + "_" ) >= 0:
			hashOrgs = copy.copy( hashCur )
			if strCur.find( "even" ) >= 0:
				d = 1.0 / len( hashOrgs )
				for strCur in hashOrgs.keys( ):
					hashOrgs[strCur] = d
			break
	if not hashOrgs:
		raise Exception( "Unknown reference: " + strPreds )
	
	hashPreds = {}
	fFirst = True
	for astrLine in csv.reader( open( strPreds ), csv.excel_tab ):
		if fFirst:
			fFirst = False
			continue
		if astrLine[0] != "#":
			break
		hashPreds[astrLine[1]] = float(astrLine[2])
	
	dAve = numpy.mean( hashPreds.values( ) )
	setstrOrgs = set(hashOrgs.keys( )) | set(hashPreds.keys( ))
	iTN = iFN = 0
	for strOrg in setstrOrgs:
		dPred = hashPreds.get( strOrg, 0 )
		if dPred >= dAve:
			continue
		if strOrg in hashOrgs:
			iFN += 1
		else:
			iTN += 1
	adNPVs.append( float(iTN) / ( iTN + iFN ) )

astrNames = [os.path.basename( s ) for s in astrPreds]
for i in range( len( astrNames ) ):
	while True:
		strIn = astrNames[i]
		for strFrom, strTo in c_hashGlosses.items( ):
			astrNames[i] = re.sub( strFrom, strTo, astrNames[i] )
		if astrNames[i] == strIn:
			break

aiSort = sorted( range( len( adNPVs ) ), cmp = lambda i, j: cmp( adNPVs[j], adNPVs[i] ) )
astrNames, adNPVs = ([a[i] for i in aiSort] for a in (astrNames, adNPVs))

print( "\t".join( astrNames ) )
print( adNPVs )

adX = numpy.arange( len( adNPVs ) ) + 0.1
pyplot.bar( adX, adNPVs, color = "k", alpha = 0.75 )
pyplot.ylabel( "NPV" )
pyplot.title( "Negative Predictive Values of Organismal Abundances" )
pyplot.xticks( adX + 0.4, astrNames )
pyplot.ylim( min( adNPVs ) * 0.9, 1 )
pyplot.savefig( strOutput, dpi = 120 )
