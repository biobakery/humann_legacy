#!/usr/bin/env python

import math
import re
import sys

# Adapted from samtools; will be occasionally inaccurate due to iteration stoppage
def incomplete_gamma( dS, dZ ):
	
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

def chi2cdf( dX, dK ):
	
	return incomplete_gamma( dK / 2.0, dX / 2.0 )

class CPathway:
	class CTree:
		
		def __init__( self, pPathway, fJoin, fOpt, pToken ):
		
			self.m_pPathway = pPathway
			self.m_fOpt = fOpt
			self.m_fJoin = fJoin
			self.m_pToken = pToken
			self.m_setGenes = set()
			if self._isleaf( ):
				self.m_setGenes.add( self.m_pToken )
			else:
				for pTree in self.m_pToken:
					self.m_setGenes |= pTree.genes( )
				
		def genes( self ):
			
			return self.m_setGenes

		def _mean( self, ad ):
	
	#		return ( ( reduce( lambda dProd, d: dProd * d, ad, 1 ) ** ( 1.0 / len( ad ) ) ) if ad else 0 )
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
		
		self.m_strID = astrTokens[0]
		self.m_setGenes = set()
		self.m_pPathway = self._parse( "+".join( ( "(" + s.replace( "-", "+-" ) + ")" ) for s in astrTokens[1:] ), False )
		self.m_setGenes = self.m_pPathway.genes( )
	
	def _parse_split( self, strToken, fJoin ):

		astrRet = []
		iParen = iPrev = iFirst = iLast = 0
		for i in range( len( strToken ) ):
			strCur = strToken[i]
			if iParen:
				if strCur == "(":
					iParen += 1
				elif strCur == ")":
					iParen -= 1
					if not iParen:
						iLast = i + 1
				continue
			if strCur == "(":
				if not iParen:
					iFirst = i
				iParen += 1
			elif strCur == ( "+" if fJoin else "," ):
				astrRet.append( strToken[iPrev:i] )
				iPrev = i + 1
		if iPrev < len( strToken ):
			astrRet.append( strToken[iPrev:] )
		if fJoin and ( iFirst == 0 ) and ( iLast == len( strToken ) ):
			astrRet[0] = astrRet[0][1:-1]
		astrRet = filter( lambda s: s, astrRet )
#		sys.stderr.write( "%s\n" % ["_parse_split", strToken, fJoin, iFirst, iLast, len( strToken ), astrRet] )
		return astrRet
		
	def _parse( self, strToken, fJoin ):

#		sys.stderr.write( "%s\n" % ["_parse", fJoin, strToken] )
		if ( strToken.find( "," ) < 0 ) and ( strToken.find( "+" ) < 0 ):
			while strToken.find( "(" ) >= 0:
				strToken = self._parse_split( strToken, " " )[0]
			fOpt = strToken[0] == "-"
			if fOpt:
				strToken = strToken[1:]
			return CPathway.CTree( self, None, fOpt, strToken )
		
		astrToken = self._parse_split( strToken, fJoin )
		return ( CPathway.CTree( self, fJoin, False, [self._parse( s, not fJoin ) for s in astrToken] )
			if ( len( astrToken ) > 1 ) else self._parse( astrToken[0], not fJoin ) )

	def id( self ):
		
		return self.m_strID
	
	def size( self ):
		
		return self.m_pPathway.size( )
	
	def genes( self ):
		
		return self.m_setGenes
	
	def coverage( self, hashGenes, dK = 0 ):

		return self.m_pPathway.coverage( hashGenes, dK )
	
	def abundance( self, hashGenes, dK = None ):
		
		return ( self.m_pPathway.abundance( hashGenes ) * ( 1 if ( dK == None ) else self.coverage( hashGenes, dK ) ) )

def open( fileIn ):

	apRet = []
	for strLine in fileIn:
		astrLine = strLine.strip( ).split( "\t" )
		apRet.append( CPathway( astrLine ) )
	return apRet
