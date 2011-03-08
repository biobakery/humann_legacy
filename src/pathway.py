#!/usr/bin/env python

import re
import sys

class CPathway:
	class CToken:
		
		def __init__( self, strToken ):
		
			self.m_setGenes = set()
			self.m_aastrGenes = []
			self.m_aafOptional = []
			for strOne in strToken.split( "|" ):
				astrGenes = filter( lambda s: s, strOne.split( "+" ) )
				if astrGenes:
					afOptional = [False] * len( astrGenes )
					for i in range( len( astrGenes ) ):
						if astrGenes[i][0] == "~":
							afOptional[i] = True
							astrGenes[i] = astrGenes[i][1:]
					self.m_aafOptional.append( afOptional )
					self.m_setGenes |= set(astrGenes)
					self.m_aastrGenes.append( astrGenes )
				
		def genes( self ):
			
			return self.m_setGenes

		def _ac( self, hashGenes, fAbundance ):

			dRet = 0			
			for astrGenes in self.m_aastrGenes:
				dCur = 0
				for strGene in astrGenes:
					d = hashGenes.get( strGene, 0 )
					dCur += d if fAbundance else ( 1 if d else 0 )
				dRet = max( float(dCur) / len( astrGenes ), dRet )
			return dRet
		
		def coverage( self, hashGenes ):

			return self._ac( hashGenes, False )
		
		def abundance( self, hashGenes ):

			return self._ac( hashGenes, True )
		
		def size( self ):

			return ( float(sum( map( lambda a: len( a ), self.m_aastrGenes ) )) / len( self.m_aastrGenes ) )
		
		def isoptional( self ):
			
			for afOptional in self.m_aafOptional:
				for fOptional in afOptional:
					if not fOptional:
						return False
			return True
		
		def __repr__( self ):
			
			return "|".join( ("+".join( ( ( "~" if af[i] else "" ) + astr[i] ) for i in range( len( astr ) ) )
				for astr, af in zip( self.m_aastrGenes, self.m_aafOptional )) )

	def __init__( self, astrTokens ):
		
		self.m_strID = astrTokens[0]
		self.m_setGenes = set()
		self.m_setTokens = set()
		for strToken in astrTokens[1:]:
			pToken = CPathway.CToken( strToken )
			if pToken.genes( ):
				self.m_setTokens.add( pToken )
				self.m_setGenes |= pToken.genes( )
		
	def id( self ):
		
		return self.m_strID
	
	def size( self ):
		
		return reduce( lambda d, p: d + p.size( ), self.m_setTokens, 0 )
	
	def genes( self ):
		
		return self.m_setGenes
	
	def _mean( self, ad ):

		return ( reduce( lambda dProd, d: dProd * d, ad, 1 ) ** ( 1.0 / len( ad ) ) )
	
	def _ac( self, hashGenes, fAbundance ):

		if not self.m_setTokens:
			return 0
		apReq = []
		apOpt = []
		for pToken in self.m_setTokens:
			( apOpt if pToken.isoptional( ) else apReq ).append( pToken )
		adReq, adOpt = ([( p.abundance if fAbundance else p.coverage )( hashGenes ) for p in a] for a in (apReq, apOpt))
		dReq = self._mean( adReq )
		if adOpt:
			dReq = self._mean( adReq + filter( lambda d: d > dReq, adOpt ) )
		return dReq
	
	def coverage( self, hashGenes ):
		
		return self._ac( hashGenes, False )
	
	def abundance( self, hashGenes ):
		
		return ( self._ac( hashGenes, True ) * self.coverage( hashGenes ) )

def open( fileIn ):

	apRet = []
	for strLine in fileIn:
		astrLine = strLine.strip( ).split( "\t" )
		apRet.append( CPathway( astrLine ) )
	return apRet
