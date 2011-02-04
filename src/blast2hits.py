#!/usr/bin/env python

import hits
import sys

c_strID		= "%identical"

strType = "blastx" if ( len( sys.argv ) <= 1 ) else sys.argv[1]
if strType in ("-h", "-help", "--help"):
	raise Exception( "Usage: blast2hits.py [type={blastx,mblastx,mapx}] [filter] < <blast.txt>" )
dFilter = 0 if ( len( sys.argv ) <= 2 ) else float(sys.argv[2])

pHits = hits.CHits( )
iID = 2 if ( strType == "blastx" ) else ( 4 if ( strType == "mblastx" ) else None )
for strLine in sys.stdin:
	astrLine = strLine.rstrip( ).split( "\t" )
	if not astrLine[0]:
		continue
	if astrLine[0].startswith( "#" ):
		if iID == None:
			for i in range( len( astrLine ) ):
				if astrLine[i] == c_strID:
					iID = i
					break
		continue
	if iID == None:
		continue
	try:
		if strType == "mblastx":
			strTo, strFrom, strID, strE, strCov = (astrLine[1], astrLine[0], astrLine[iID],
				astrLine[2], astrLine[5])
		elif strType == "mapx":
			strTo, strFrom, strID, strE, strCov = (astrLine[0], astrLine[2], astrLine[iID],
				astrLine[-1], astrLine[iID + 1])
		else:
			strTo, strFrom, strID, strE, strCov = (astrLine[1], astrLine[0], astrLine[iID],
				astrLine[-2], astrLine[3])
	except IndexError:
		sys.stderr.write( "%s\n" % astrLine )
		continue
	try:
		dE, dID, dCov = (float(s) for s in (strE, strID, strCov))
	except ValueError:
		continue
	if dFilter > 0:
		if ( dID / 100 ) >= dFilter:
			continue
	pHits.add( strTo, strFrom, dE, dID, dCov )
pHits.save( sys.stdout )
