#!/usr/bin/env python

import math
import re
import sys


# Adapted from samtools; will be occasionally inaccurate due to iteration stoppage
def incomplete_gamma1( dS, dZ ):
	
	dS, dZ = (float(d) for d in (dS, dZ))
	dSum = dX = 1
	for i in xrange( 1, 10000 ):
		dX *= dZ / ( dS + i )
		dSum += dX
		if ( dX / dSum ) < 1e-14:
			break
	return ( math.exp( ( dS * math.log( dZ ) ) - dZ - _log_gamma( dS + 1 ) + math.log( dSum ) ) if dZ else 0 )

def _log_gamma( dZ ):
	
	dX = 0
	dX += 0.1659470187408462e-06 / ( dZ + 7 )
	dX += 0.9934937113930748e-05 / ( dZ + 6 )
	dX -= 0.1385710331296526     / ( dZ + 5 )
	dX += 12.50734324009056      / ( dZ + 4 )
	dX -= 176.6150291498386      / ( dZ + 3 )
	dX += 771.3234287757674      / ( dZ + 2 )
	dX -= 1259.139216722289      / ( dZ + 1 )
	dX += 676.5203681218835      / dZ
	dX += 0.9999999999995183;
	return ( math.log( dX ) - 5.58106146679532777 - dZ + ( ( dZ - 0.5 ) * math.log( dZ + 6.5 ) ) )

# Implementation thanks to http://www.crbond.com/math.htm thanks to Zhang and Jin
# Modified to only return normalized/regularized lower incomplete gamma
def incomplete_gamma2( dA, dX ):

	if ( dA < 0 ) or ( dX < 0 ):
		return None
	if not dX:
		return 0
	xam = -dX + dA * math.log( dX )
	if ( xam > 700 ) or ( dA > 170 ):
		return 1
	if dX <= ( dA + 1 ):
		r = s = 1.0 / dA
		for k in range( 1, 61 ):
			r *= float(dX) / ( dA + k )
			s += r
			if abs( r / s ) < 1e-15:
				break
		ga = math.gamma( dA )
		gin = math.exp( xam ) * s
		return ( gin / ga )

	t0 = 0
	for k in range( 60, 0, -1 ):
		t0 = float(k - dA) / ( 1 + ( float(k) / ( dX + t0 ) ) )
	gim = math.exp( xam ) / ( dX + t0 )
	ga = math.gamma( dA )
	return ( 1 - ( gim / ga ) )

#for dX, dY in ((1, 1), (1, 2), (2, 1), (3, 4), (5, 10), (40, 2636)):
#	print( "\t".join( (str(d) for d in (incomplete_gamma( dX, dY ), incomplete_gamma2( dX, dY ))) ) )
#sys.exit( 0 )

def chi2cdf( dX, dK ):
	
	dK, dX = (( d / 2 ) for d in (dK, dX))
	dRet = incomplete_gamma1( dK, dX )
#   Ugh - there's no better way to do this in Python 2?
#	if abs( dRet ) != float("Inf"):
#		return dRet
	if abs( dRet ) != float("Inf"):
		return dRet
	return incomplete_gamma2( dK, dX )

class CPathway:
	class CTree:
		
		def __init__( self, pPathway, fJoin, fOpt, pToken ):
		
			# Load variables passed in into member variables.
			self.m_pPathway = pPathway
			self.m_fOpt = fOpt
			self.m_fJoin = fJoin
			self.m_pToken = pToken
			self.m_setGenes = set()
			if self._isleaf( ): # If m_pToken is a string, add it to the set m_setGenes.
				self.m_setGenes.add( self.m_pToken )
			else:
				for pTree in self.m_pToken:
					self.m_setGenes |= pTree.genes( ) # Loop through the whole tree and load all of the genes in all of the sets of the tree into the set setGenes.
				
		def genes( self ):
			"""
			Return the set of genes associated with member variable m_setGenes.
			"""

			return self.m_setGenes

		def _mean( self, ad ):

			return ( ( len( ad ) / sum( ( 1.0 / d ) for d in ad ) ) if ( ad and ( min( ad ) > 0 ) ) else 0 )
		
		def _reqopt( self, adReq, adOpt ):
	
			dRet = self._mean( adReq )
			if adOpt:
				dRet = self._mean( adReq + filter( lambda d: d > dRet, adOpt ) )
			return dRet

		def _ac( self, hashGenes, fAbundance, dK = 0 ):
			
			if self._isleaf( ):
				d = hashGenes.get( self.m_pToken, 0 )
				if not fAbundance:
					d = chi2cdf( d, dK ) if dK else ( 1 if d else 0 )
				return d
			
			adReq = []
			adOpt = []
			for pChild in self.m_pToken:
				( adOpt if pChild.m_fOpt else adReq ).append( pChild._ac( hashGenes, fAbundance, dK ) )
			return ( self._reqopt( adReq, adOpt ) if self.m_fJoin else max( adReq + adOpt ) )
		
		def coverage( self, hashGenes, dK = 0 ):

			return self._ac( hashGenes, False, dK )
		
		def abundance( self, hashGenes, dK = None ):

			return self._ac( hashGenes, True )

		def _isleaf( self ):
			"""
			Returns true if m_pToken member variable is a string.
			"""
			
			return isinstance( self.m_pToken, str )
		
		def size( self ):
			
			if self._isleaf( ):
				return ( 0 if self.m_fOpt else 1 )
			
			dSum = sum( pTree.size( ) for pTree in self.m_pToken )
			return ( dSum if self.m_fJoin else ( dSum / len( filter( lambda p: not p.m_fOpt, self.m_pToken ) ) ) )
		
		def __repr__( self ):

			if self._isleaf( ):
				return ( ( "~" if self.m_fOpt else "" ) + self.m_pToken )
			
			return ( "(" + ( "+" if self.m_fJoin else "," ).join( str(p) for p in self.m_pToken ) + ")" )

	def __init__( self, astrTokens ):
		"""
		Loads member variables from a line of the file passed in to pathway.open( ). See open( ) function definition below.
		"""

		self.m_strID = astrTokens[0] # Object in the first column is the ID (a KO pathway or module ID).
		self.m_setGenes = set() # m_setGenes is a set for holding unique genes.
		# For each KO in the pathway currently examined (the current line), replace any dashes with a plus followed by a dash, enclose each KO ID in parentheses, and join all of the resulting parentheticals with pluses.
		self.m_pPathway = self._parse( "+".join( ( "(" + s.replace( "-", "+-" ) + ")" ) for s in astrTokens[1:] ) , False )	# Then take those plus-separated parenthetical KOs and pass them into the ._parse method.
		
		self.m_setGenes = self.m_pPathway.genes( )
	
	def _parse_split( self, strToken, fJoin ):
		"""
		Takes in a string and returns and array of all the things in that string which are separated by parentheses.
		"""
		astrRet = [] # Holds an array of all of the items in the passed in string (strToken) which are surrounded by parentheses.
		iParen = iPrev = iFirst = iLast = 0 # iParen counts the number of parentheses currently open. iFirst is the index of the first open parenthesis, iLast is the index of the last closing parenthesis. iPrev records the index of the first character after the last group to be added to astrRet.
		for i in range( len( strToken ) ): # Loop through each character in the passed-in string.
			strCur = strToken[i] # strCur is the character currently being examined.
			if iParen: # If there is at least one open parenthesis already:
				if strCur == "(":
					iParen += 1
				elif strCur == ")":
					iParen -= 1
					if not iParen: # If closing this parenthesis means no more parentheses are open, then set iLast to the index of the first character outside the parenthesis.
						iLast = i + 1
				continue # If a parenthesis is open, then at this point go to next character in the passed-in string.
			if strCur == "(": # If there is not an open parenthesis yet, but this character is a parenthesis:
				if not iParen:
					iFirst = i # Then its index is the start index of the parenthesis, iFirst.
				iParen += 1 # Increment the open parenthesis counter by one.
			elif strCur == ( "+" if fJoin else "," ): # If no parentheses are open and the current character is a plus (if the fJoin option was passed in as true) or a comma (if the fJoin option was not passed in as true).
				astrRet.append( strToken[iPrev:i] ) # Then add an entry to astrRet consisting of all the characters from the end of the last parenthetical group to this one.
				iPrev = i + 1 # Reset the counter of where the last added entry ended to be the character after this one.
		if iPrev < len( strToken ): # If, after the above loop, some words were added, then add everything from the end of the last word to the end of the string to astrRet.
			astrRet.append( strToken[iPrev:] )
		if fJoin and ( iFirst == 0 ) and ( iLast == len( strToken ) ): # If the fJoin flag is true, and there were parentheses around the entire string passed in:
			astrRet[0] = astrRet[0][1:-1] # Then remove the last character from the first entry of astrRet.
		astrRet = filter( lambda s: s, astrRet ) # Remove any blank or null entries from astrRet.
#		sys.stderr.write( "%s\n" % ["_parse_split", strToken, fJoin, iFirst, iLast, len( strToken ), astrRet] )
		return astrRet
		
	def _parse( self, strToken, fJoin ):

#		sys.stderr.write( "%s\n" % ["_parse", fJoin, strToken] )
		if ( strToken.find( "," ) < 0 ) and ( strToken.find( "+" ) < 0 ): # If there are no commas and no pluses in the string passed in:
			while strToken.find( "(" ) >= 0: # While the string passed in still has open parentheses:
				strToken = self._parse_split( strToken, " " )[0] # Sets strToken equal to the the first occurance in strToken of a string which is surrounded by parentheses.
			# This loop essentially cuts into multiple-parentheticals until it gets to the core of the deepest parenthetical.
			fOpt = strToken[0] == "-" # fOpt is true if the first character in the parentheses-striped string passed in (strToken) is a dash.
			if fOpt:
				strToken = strToken[1:] # If there is such a leading dash, remove it.
			return CPathway.CTree( self, None, fOpt, strToken ) # Make a call to the CTree class.
		# If there are commas or pluses in the string passed in:
		astrToken = self._parse_split( strToken, fJoin )
		return ( CPathway.CTree( self, fJoin, False, [self._parse( s, not fJoin ) for s in astrToken] )
			if ( len( astrToken ) > 1 ) else self._parse( astrToken[0], not fJoin ) )

	def id( self ):
		""" Returns the member variable containing the KEGG ID of the pathway currently under examination (m_strID). """

		return self.m_strID
	
	def size( self ):
		""" Returns the number of genes in the pathway currently under examination (member variable m_pPathway). """

		return self.m_pPathway.size( )
	
	def genes( self ):
		""" Returns the member variable m_setGenes. """
		
		return self.m_setGenes
	
	def coverage( self, hashGenes, dK = 0 ):

		return self.m_pPathway.coverage( hashGenes, dK )
	
	def abundance( self, hashGenes, dK = None ):
		
		return ( self.m_pPathway.abundance( hashGenes ) * ( 1 if ( dK == None ) else self.coverage( hashGenes, dK ) ) )

def open( fileIn ):
	"""
	Reads every line in an input file (fileIn), returns an array of pointers to CPathway objects, one for each line.
	Inputs: a file (fileIn) each line of which is to be turned into a CPathway object.
	Outputs: an array of pointers to CPathway objects (apRet), one for each line in fileIn.
	"""

	apRet = [] # Array holding pointers to CPathway objects, one CPathway per line in the input file.
	for strLine in fileIn: # Loop through every line of the input file.
		astrLine = strLine.strip( ).split( "\t" ) # Split each line by tabs.
		apRet.append( CPathway( astrLine ) ) # Instantiate a CPathway object for each line in the input file, append each CPathway object to the growing array of pointers apRet
	return apRet # Return an array of pointers to CPathway objects, one for each line in fileIn.
