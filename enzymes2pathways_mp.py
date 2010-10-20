#!/usr/bin/env python

import os
import subprocess
import sys
import tempfile

c_strDirMinPath	= "./MinPath/"
c_strMinPath	= "MinPath1.1hmp.py"

hashAbs = {}
astrComments = []
iIn, strIn = tempfile.mkstemp( )
for strLine in sys.stdin:
	if strLine and ( strLine[0] == "#" ):
		astrComments.append( strLine )
		continue
	strID, strAb = strLine.strip( ).split( "\t" )
	if strID == "GID":
		continue
	hashAbs[strID] = d = float(strAb)
	os.write( iIn, "%s	%g\n" % (strID, d) )
os.close( iIn )

iOut, strOut = tempfile.mkstemp( )
iTmp, strTmp = tempfile.mkstemp( )
os.close( iOut )
subprocess.call( [c_strDirMinPath + c_strMinPath, "-ko", strIn, "-report",
	"/dev/null", "-details", strOut, "-mps", strTmp],
	env = {"MinPath": c_strDirMinPath}, stdout = sys.stderr )
os.unlink( strIn )

strPath = None
hashPaths = {}
for strLine in open( strOut ):
	astrLine = strLine.strip( ).split( " " )
	if strLine[0:4] == "path":
		strPath = astrLine[1]
	else:
		hashPaths.setdefault( astrLine[0], [] ).append( strPath )
os.unlink( strOut )

print( "GID	Pathway	Abundance" )
sys.stdout.write( "".join( astrComments ) )
for strID, dAb in hashAbs.items( ):
	astrPaths = hashPaths.get( strID ) or [""]
	strAb = str(dAb) # / len( astrPaths ))
	for strPath in ( astrPaths or [""] ):
		if len( strPath ) > 0:
			strPath = "ko" + strPath
		print( "\t".join( [strID, strPath, strAb] ) )
