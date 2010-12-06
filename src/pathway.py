#!/usr/bin/env python

class CPathway:

	def __init__( self, astrTokens ):
		
		self.m_strID = astrTokens[0]
		self.m_setGenes = set()
		self.m_asetTokens = []
		for strToken in astrTokens[1:]:
			astrToken = strToken.split( "|" )
			self.m_asetTokens.append( set(astrToken) )
			for strGene in astrToken:
				self.m_setGenes.add( strGene )
		
	def id( self ):
		
		return self.m_strID
	
	def tokens( self ):
		
		return self.m_asetTokens
	
	def genes( self ):
		
		return self.m_setGenes
	
	def coverage( self, hashGenes ):
		
		if not self.m_asetTokens:
			return 0
		
		iHits = 0
		for setToken in self.m_asetTokens:
			for strGene in setToken:
				if hashGenes.get( strGene ):
					iHits += 1
					break
		return ( float(iHits) / len( self.m_asetTokens ) )

def open( fileIn ):

	apRet = []
	for strLine in fileIn:
		astrLine = strLine.strip( ).split( "\t" )
		apRet.append( CPathway( astrLine ) )
	return apRet
