#!/usr/bin/env python

import re
import sys

class CPathway:
	class CToken:
		
		def __init__( self, strToken ):
			
			self.m_setGenes = set()
			self.m_aastrGenes = []
			for strOne in strToken.split( "|" ):
				astrGenes = filter( lambda s: s, strOne.split( "+" ) )
				if astrGenes:
					self.m_setGenes |= set(astrGenes)
					self.m_aastrGenes.append( astrGenes )
				
		def genes( self ):
			
			return self.m_setGenes
		
		def coverage( self, hashGenes ):

			dRet = 0			
			for astrGenes in self.m_aastrGenes:
				iCur = reduce( lambda i, s: i + ( 1 if hashGenes.get( s ) else 0 ), astrGenes, 0 )
				dRet = max( float(iCur) / len( astrGenes ), dRet )
			return dRet
		
		def abundance( self, hashGenes ):

			dRet = 0
			for astrGenes in self.m_aastrGenes:
				dCur = reduce( lambda i, s: i + hashGenes.get( s, 0 ), astrGenes, 0 )
				dRet = max( dCur / len( astrGenes ), dRet )
			return dRet
		
		def size( self ):

			return ( float(sum( map( lambda a: len( a ), self.m_aastrGenes ) )) / len( self.m_aastrGenes ) )

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
	
	def coverage( self, hashGenes ):
		
		if not self.m_setTokens:
			return 0
		dRet = reduce( lambda d, p: d + p.coverage( hashGenes ), self.m_setTokens, 0 )
		return ( dRet / len( self.m_setTokens ) )
	
	def abundance( self, hashGenes ):
		
		if not self.m_setTokens:
			return 0
		dRet = reduce( lambda d, p: d + p.abundance( hashGenes ), self.m_setTokens, 0 )
		return ( dRet / len( self.m_setTokens ) )

def open( fileIn ):

	apRet = []
	for strLine in fileIn:
		astrLine = strLine.strip( ).split( "\t" )
		apRet.append( CPathway( astrLine ) )
	return apRet
