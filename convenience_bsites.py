#!/usr/bin/env python

import re
import sys

c_strBM		= "Buccal_mucosa"
c_strSP		= "Supragingival_plaque"
c_strAN		= "Anterior_nares"
c_strTD		= "Tongue_dorsum"
c_strST		= "Stool"
c_strRAC	= "R_Retroauricular_crease"
c_strPF		= "Posterior_fornix" 
c_hashBSites	= {
	"700024400"	: c_strBM,
	"700024407"	: c_strAN,
	"700024410"	: c_strSP,
	"700024417"	: c_strTD,
	"700024437"	: c_strST,
	"700037036"	: c_strBM,
	"700037040"	: c_strSP,
	"700038583"	: c_strBM,
	"700038587"	: c_strSP,
	"700038590"	: c_strRAC,
	"700038593"	: c_strAN,
	"700038594"	: c_strST,
	"700038600"	: c_strTD,
	"700106278"	: c_strTD,
	"700106433"	: c_strAN,
	"700106436"	: c_strPF,
	"700106440"	: c_strTD,
	"700106442"	: c_strBM,
	"700106446"	: c_strSP,
	"700106465"	: c_strST,
}

def bsite( strCondition ):

	for strToken in re.split( '\s+', strCondition ):
		strRet = c_hashBSites.get( strToken )
		if strRet:
			return ( strRet + " " + strCondition ) 
		
	return strCondition

fFirst = True
for strLine in sys.stdin:
	sys.stdout.write( strLine )
	if fFirst:
		fFirst = False
		astrLine = strLine.rstrip( ).split( "\t" )
		astrLine[0] = "body_site"
		for i in range( len( astrLine ) ):
			astrLine[i] = bsite( astrLine[i] )
		print( "\t".join( astrLine ) )
