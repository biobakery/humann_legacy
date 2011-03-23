#!/usr/bin/env python

import math
import re
import sys

# Implementation thanks to http://www.crbond.com/math.htm thanks to Zhang and Jim
def incomplete_gamma( dA, dX ):

	if ( dA < 0 ) or ( dX < 0 ):
		return None
	if not dX:
		return (0, math.gamma( dA ), 0)
	xam = -dX + dA * math.log( dX )
	if ( xam > 700 ) or ( dA > 170 ):
		return None
	if dX <= ( dA + 1 ):
		r = s = 1.0 / dA
		for k in range( 1, 61 ):
			r *= float(dX) / ( dA + k )
			s += r
			if abs( r / s ) < 1e-15:
				break
		ga = math.gamma( dA )
		gin = math.exp( xam ) * s
		return (gin, ga - gin, gin / ga)

	t0 = 0
	for k in range( 60, 0, -1 ):
		t0 = float(k - dA) / ( 1 + ( float(k) / ( dX + t0 ) ) )
	gim = math.exp( xam ) / ( dX + t0 )
	ga = math.gamma( dA )
	return (ga - gim, gim, 1 - ( gim / ga ))

def chi2cdf( dX, dK ):
	
	adIG = incomplete_gamma( dK / 2.0, dX / 2.0 )
	return ( adIG[-1] if adIG else None )

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
			return ( ( len( ad ) / sum( ( 1.0 / d ) for d in ad ) ) if ( ad and min( ad ) ) else 0 )
		
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
