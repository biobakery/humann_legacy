#!/usr/bin/env python

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
for strLine in sys.stdin:
	strPath, strCov = strLine.strip( ).split( "\t" )
	if strPath == "PID":
		continue
	hashPaths[strPath] = float(strCov)
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

print( "PID	Coverage" )
for strPath, dCov in hashPaths.items( ):
	if dCov:
		print( "\t".join( (strPath, "%g" % dCov) ) )
