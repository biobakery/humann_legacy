#!/usr/bin/env python

import matplotlib
matplotlib.use( "Agg" )
from matplotlib import pyplot
import csv
import math
import numpy
import re
import scipy.stats
import sklearn.metrics
import sys

c_dFPR			= 0.1
c_astrCoverage	= ("Coverage", "Abundance")
c_astrLabels	= ("pAUC(%g)" % c_dFPR, "Correlation (asin sqrt)")
c_ahashGlosses	= [
	None, # hit
	{"kab" : "-log(BS)", "kgo" : "BBH", "kga" : "PVal"},
	{"mpm" : "+MP", "nve" : "-MP"},
	{"nul" : "-Tax", "nve" : "+TaxC", "nuc" : "+Tax"},
#	{"wbl" : "+SmWB", "nul" : "-Sm"},
	{"nve" : "+GF", "nul" : "-GF"},
	None, # Ab/Cov
	None, # Xipe
]
c_astrTarget	= ["PVal", "+MP", "+TaxC", "-Sm", "+GF"]

def funcTransform( adData ):
	
	return [math.asin( d ** 0.5 ) for d in adData]

def funcPerf( fAUC, adGS, adData ):
	
	if fAUC:
		adFPR, adTPR, adThresholds = sklearn.metrics.roc_curve( numpy.array( adGS ), numpy.array( adData ) )
#		dRet = sklearn.metrics.auc( adFPR, adTPR )
		dRet = dTPR = dFPR = 0
		for i in range( len( adFPR ) ):
			if adFPR[i] > c_dFPR:
				d = dTPR + ( ( adTPR[i] - dTPR ) * ( c_dFPR - dFPR ) / ( adFPR[i] - dFPR ) )
				dRet += ( c_dFPR - dFPR ) * ( dTPR + d ) / 2
				break
			dRet += ( adFPR[i] - dFPR ) * ( dTPR + adTPR[i] ) / 2
			dTPR, dFPR = (a[i] for a in (adTPR, adFPR))
		dRet /= c_dFPR
	else:
		dR, dP = scipy.stats.pearsonr( funcTransform( adGS ), funcTransform( adData ) )
		dRet = dR

	return dRet

def funcGloss( strData ):
	
	astrData = strData.split( "-" )
	astrRet = []
	for i in range( min( len( astrData ), len( c_ahashGlosses ) ) ):
		hashCur = c_ahashGlosses[i]
		if hashCur != None:
			astrRet.append( hashCur.get( astrData[i], astrData[i] ) )
	return "\n".join( astrRet )

if len( sys.argv ) < 3:
	raise Exception( "Usage: performance.py <metadatum> <output.png> <mocks.txt>+" )
strMetadatum, strOutput, astrMocks = sys.argv[1], sys.argv[2], sys.argv[3:]

# evaluation has coverage, moduleset, 
ahashPerfs = [None] * len( c_astrCoverage )
for i in range( len( ahashPerfs ) ):
	ahashPerfs[i] = {}
for strMock in astrMocks:
	mtch = re.search( r'\d{2}([a-z])\.\S+$', strMock )
	fCoverage = mtch and ( mtch.group( 1 ) == "a" )
	astrTypes = fData = None
	hashFeatures = {}
	for astrLine in csv.reader( open( strMock ), csv.excel_tab ):
		strID, strName, astrData = astrLine[0], astrLine[1], astrLine[2:]
		if astrTypes:
			if fData:
				adData = [float(s) for s in astrData]
				hashFeatures.setdefault( strID[0], [] ).append( [strID, strName, adData] )
			elif strID == strMetadatum:
				fData = True
		else:
			astrTypes = astrData
	aadData = []
	for strFeature, aaFeatures in hashFeatures.items( ):
		fKeep = False
		for aFeature in aaFeatures:
			dMax = max( aFeature[2][1:] )
			if dMax:
				fKeep = True
				break
		if fKeep:
			aadData.extend( a[2] for a in aaFeatures )
	adGS = [a[0] for a in aadData]
	for iType in range( 1, len( astrTypes ) ):
		strType = astrTypes[iType].replace( astrTypes[0], "" )[1:]
		dPerf = funcPerf( fCoverage, adGS, [a[iType] for a in aadData] )
		ahashPerfs[0 if fCoverage else 1].setdefault( strType, [] ).append( dPerf )

for iPlot in range( len( ahashPerfs ) ):
	iPerf = len( ahashPerfs ) - iPlot - 1
	hashPerf = ahashPerfs[iPerf]
	strCoverage = c_astrCoverage[iPerf]
	aadBoxes = []
	aastrPerfs = sorted( hashPerf.items( ) )
	for astrPerf in aastrPerfs:
		strType, adType = astrPerf
		aadBoxes.append( adType )
		dAve = numpy.mean( adType )
		dStd = numpy.std( adType )
		sys.stderr.write( "%s\n" % [strCoverage, strType, dAve, dStd] )

	if not iPlot:
		iHeight = 3
		pyplot.figure( figsize = (iHeight * len( aadBoxes ) / 2, iHeight) )
		pyplot.subplots_adjust( left = 0.075, right = 0.99, bottom = 0.2 )
	pyplot.subplot( 1, len( ahashPerfs ), iPlot + 1 )
	pBP = pyplot.boxplot( aadBoxes, notch = 1, sym = "k.", patch_artist = True )
	for s in ("whiskers", "fliers"):
		pyplot.setp( pBP[s], color = "k" )
	pyplot.setp( pBP["boxes"], edgecolor = "k", color = "w" )
	pyplot.setp( pBP["medians"], color = "gray" )
	pyplot.title( strCoverage )
	pyplot.ylabel( c_astrLabels[iPerf] )
	astrLabels = [funcGloss( a[0] ) for a in aastrPerfs]
	try:
		i = astrLabels.index( "\n".join( c_astrTarget ) )
		pyplot.setp( pBP["boxes"][i], color = "#CCCCCC", edgecolor = "k" )
	except ValueError:
		pass
	pyplot.gca( ).set_xticklabels( astrLabels, size = "x-small" )
pyplot.savefig( strOutput, dpi = 120 )
