#!/usr/bin/env python

import subprocess
import sys

c_dPerc			= 0.25
c_dProb			= 0.9

if len( sys.argv ) < 2:
	raise Exception( "Usage: trim_xp.py <xipe.py> [perc=%g] [prob=%g] < <pathways.txt>" %
		(c_dPerc, c_dProb) )
strXipe = sys.argv[1]
dPerc = float(sys.argv[2]) if ( len( sys.argv ) > 2 ) else c_dPerc
dProb = float(sys.argv[3]) if ( len( sys.argv ) > 3 ) else c_dProb

hashhashPaths = {}
for strLine in sys.stdin:
	strGene, strPath, strAb = strLine.strip( ).split( "\t" )
	if strGene == "GID":
		continue
	hashhashPaths.setdefault( strPath, {} )[strGene] = float(strAb)

for strPath, hashPath in hashhashPaths.items( ):
	sys.stderr.write( "Pathway: %s\n" % strPath )
	
	strGenes = ""
	for strGene, dAb in hashPath.items( ):
		strGenes += "%s	%g\n" % (strGene, dAb)
	procXipe = subprocess.Popen( [c_strXipe, "--file2", str(dPerc)], stdin = subprocess.PIPE,
		stdout = subprocess.PIPE, stderr = subprocess.PIPE )
	strOut, strErr = procXipe.communicate( strGenes )

	setBad = set()
	for strLine in strErr.split( "\n" ):
		astrLine = strLine.strip( ).split( "\t" )
		if len( astrLine ) < 2:
			continue
		strMsg, strKey = astrLine
		setBad.add( strKey )
	for strLine in strOut.split( "\n" ):
		astrLine = strLine.strip( ).split( "\t" )
		if len( astrLine ) < 2:
			continue
		strKey, strTuple = astrLine
		if strKey not in setBad:
			continue
		strScore, strBin = strTuple[1:-1].split( ", " )
		if ( float(strScore) >= dProb ) and ( int(strBin) == 1 ):
			setBad.remove( strKey )
	sys.stderr.write( "Removing: %s\n" % setBad )
	for strGene in setBad:
		hashPath[strGene] = 0

print( "GID	Pathway	Abundance" )
for strPath, hashPath in hashhashPaths.items( ):
	for strGene, dAb in hashPath.items( ):
		if dAb:
			print( "\t".join( (strGene, strPath, "%g" % dAb) ) )
