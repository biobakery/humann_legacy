#!/usr/bin/env python

"""
Description:
Step in the pipeline: 03c to 04a.
Program called before: pathcov.py.
Program called after: None, or performance.py.
"""

import subprocess
import sys

c_dPerc			= 0.1
c_dProb			= 0.9

if len( sys.argv ) < 2:
	raise Exception( "Usage: pathcov_xp.py <xipe.py> [perc=%g] [prob=%g] < <pathways.txt>" %
		(c_dPerc, c_dProb) )
strXipe = sys.argv[1]
dPerc = float(sys.argv[2]) if ( len( sys.argv ) > 2 ) else c_dPerc
dProb = float(sys.argv[3]) if ( len( sys.argv ) > 3 ) else c_dProb

hashPaths = {}
hashhashPaths = {}
for strLine in sys.stdin: # Loop through the lines in the input file (an 03c format file).
	astrLine = strLine.strip( ).split( "\t" ) # Split each line by tabs into an array.
	if astrLine[0] == "PID": # If this line is the header line:
		fOrg = len( astrLine ) > 2 # If the headers are three columns or more, then this is an organism-specific file.
		continue
	hashhashPaths.setdefault( astrLine[1] if fOrg else None, {} )[astrLine[0]] = float( astrLine[2] ) if fOrg else float( astrLine[1] )
sys.stdout.write( "PID	" )
if fOrg:
	sys.stdout.write( "Organism	" )
print( "Coverage" )
for strOrg, hashPaths in hashhashPaths.items( ):
	procXipe = subprocess.Popen( [strXipe, "--file2", str(dPerc)], stdin = subprocess.PIPE,
		stdout = subprocess.PIPE, stderr = subprocess.PIPE )
	strOut, strErr = procXipe.communicate( "\n".join( "\t".join( str(strCur) for strCur in astrCur )
		for astrCur in hashPaths.items( ) ) )

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
	for strPath in setBad:
		hashPaths[strPath] = 0

	for strPath, dCov in hashPaths.items( ):
		if dCov:
			if fOrg:
				print( "\t".join( (strPath, strOrg, "%g" % dCov) ) )
			else:
				print( "\t".join( (strPath, "%g" % dCov) ) )
