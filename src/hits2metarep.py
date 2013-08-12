#!/usr/bin/env python

import array
import hits # Part of HUMAnN, see hits.py located in src dir.
import math
import re
import sys

def median( ad ):
	""" Returns the median of the inputed array. """
	return ad[int(len( ad ) / 2)] # Returns the median of the ad array.

strGeneLs = None if ( len( sys.argv ) <= 1 ) else sys.argv[1] # strGeneLs is the first commandline arguement if it exists.
if strGeneLs in ("-h", "-help", "--help"):
	raise Exception( "Usage: hits2metarep.py [genels] < <hits.bin>" ) # If user flags input for help, return usage instructions.

pHits = hits.CHits( ) # Instantiate a CHits object from the hits library (see hits.py), point to it with pHits.
try:
	pHits.open( sys.stdin ) # Try to unpickle variables from the standard inputed (piped in) file.
except IndexError:
	sys.stderr.write( "Invalid input hits file; did you provide at least one BLAST hit using the correct gene identifiers?\n" )
	sys.exit( -1 ) # If unable to open the stdin file, print an error and exit with error status -1.

hashGeneLs = {} # Dict containing all of the genes in the input file, normalized by the average length of all genes in the input file.
if strGeneLs:
	astrGenes = [] # Array holds the gene id of every gene appearing in the input file.
	aiGenes = [] # Array holds the length of every gene appearing in the input file.
	dAve = 0
	for strLine in open( strGeneLs ): # Open the strGeneLs file.
		strGene, strLength = strLine.strip( ).split( "\t" ) # Split the two columns by tab, let strGene be the first column strLength be the second column.
		astrGenes.append( strGene ) # Add the gene id to the array of gene ids.
		iLength = int(strLength) # Convert the gene length from the second column to an integer.
		aiGenes.append( iLength ) # Load the gene length integer into an array containing all gene lengths.
		dAve += iLength # Add the most recent gene to a counter storing the length of all the genes combined (to be averaged later).
	dAve /= float(len( astrGenes )) # Divide the total combined length of all the genes by the total number of genes to get the average length of the genes in the input file.
	for i in range( len( astrGenes ) ):
		hashGeneLs[astrGenes[i]] = aiGenes[i] / dAve # Load into the hashGenesLs dict the length of every gene normalized by the average length of all the genes in the file.

pAbundances = array.array( "f", (0 for i in range( pHits.get_tos( ) )) ) # Instantiates an array of zeros the length of the m_astrTos member variable of pHits.
apScores = []
for i in range( pHits.get_tos( ) ): # Once for every entry in the m_astrTos member variable:
	apScores.append( array.array( "L" ) ) # Append a blank array of unsigned long numbers to apScores.
for iFrom in range( pHits.get_froms( ) ): # Once for every entry in the m_astrFroms member variable:
	aiScores = pHits.get_scores( iFrom ) # Retrieve the value in the m_apScores member variable corresponding to the the current entry in the m_astrFroms member variable.
	aiTos = [pHits.get_scoreto( i ) for i in aiScores] # Loads aiTos array with value of member variable m_pTos corresponding to the values of the integers in aiScores.
	aiIndices = filter( lambda i: pHits.get_to( aiTos[i] ).find( ":" ) >= 0, range( len( aiTos ) ) ) # Makes a list of the indices of aiTos for which m_astrTos contains a ':'
	aiScores, aiTos = ([a[i] for i in aiIndices] for a in (aiScores, aiTos)) # aiScores and aiTos are filled only with values which include a ':' (all entries NOT corresponding to entries in aiIindices are removed).
	aadScores = [pHits.get_dic( i ) for i in aiScores] # For each value in aiScores (which all must have a ':'), return an array of the tuples (m_pEs, m_pIDs, m_pCovs) at each value of i.
	dSum = sum( math.exp( -a[0] ) for a in aadScores ) # dSum is 10^(-pEs[0]) + 10^(-pIDs[0]) + 10^(-pCovs[0]) - Note it is for the first tuple in the aadScores tuple only.
	for i in range( len( aiScores ) ): # Loop through integer indices up to the length of aiScores.
		iTo, adCur = (a[i] for a in (aiTos, aadScores)) # iTo = aiTos[i], adCur = aadScores[i]
		# adCur is of the form [float from 0 to 1.0, 1.0, 1.0]
		strTo = pHits.get_to( iTo ) # strTo receives the value of the m_astrTos corresponding to the iTo index.
		# strTo is of the form ddr:Deide_03340
		strTo = re.sub( r'\s+.*$', "", strTo ) # Delete any appearances of this regular expression in strTo.
		dScore = math.exp( -adCur[0] ) / hashGeneLs.get( strTo, 1 ) # 10^(-adCur[0]) / length of gene normalized by the average length of all genes
		pAbundances[iTo] += dScore / ( dSum or 1 )
		apScores[iTo].append( aiScores[i] ) # Load the apScores array at the index iTo with the value of aiScores at the current i.
		#apScores now of the form array('L') with sparse entries of the form array('L', [1749L]) and occasionally entries of the form array('L', [3465L, 2345L])

for iTo in range( len( pAbundances ) ):
	aadScores = [pHits.get_dic( i ) for i in apScores[iTo]] # For each value in apScores, return an array of the tuples (m_pEs, m_pIDs, m_pCovs) at each value of i. These correspond to (e-values, IDs, Coverages)
	# TODO Keep an eye on this code. The code works if aadScores is passed an array with values in it, but if any of the blank entries in apScores are passed get_dic then aadScores will not be constructed properly and an error will result downstream.
	adScores = [median( sorted( aadScores[i][j] for i in range( len( aadScores ) ) ) ) for j in range( len( aadScores[0] ) )]
	print( "\t".join( [pHits.get_to( iTo )] + [( "%g" % d ) for d in ( [pAbundances[iTo]] +
		adScores )] ) )
