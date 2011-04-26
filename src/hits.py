#!/usr/bin/env python

import array
import pickle
import sys

class CHits:

	def __init__( self ):

		self._clear( )

	def _clear( self ):
				
		self.m_hashFroms = {}
		self.m_hashTos = {}
		self.m_astrTos = []
		self.m_astrFroms = []
		self.m_apScores = []
		self.m_pTos = array.array( "L" )
		self.m_pEs = array.array( "f" )
		self.m_pIDs = array.array( "f" )
		self.m_pCovs = array.array( "f" )
		
	def _enhash( self, strID, hashIDs, astrIDs, apScores = None ):
	
		iID = hashIDs.get( strID )
		if iID == None:
			hashIDs[strID] = iID = len( hashIDs )
			astrIDs.append( strID )
			if apScores != None:
				apScores.append( array.array( "L" ) )
			
		return iID

	def _repopulate( self, astrIDs, hashIDs ):
		
		for i in range( len( astrIDs ) ):
			hashIDs[astrIDs[i]] = i

	def add( self, strTo, strFrom, dE, dID, dCov ):
		
		for astrCur, hashCur in ((self.m_astrTos, self.m_hashTos), (self.m_astrFroms, self.m_hashFroms)):
			if astrCur and ( not hashCur ):
				self._repopulate( astr, hash )

		iTo = self._enhash( strTo, self.m_hashTos, self.m_astrTos )
		iFrom = self._enhash( strFrom, self.m_hashFroms, self.m_astrFroms, self.m_apScores )
		iScore = len( self.m_pTos )
		self.m_apScores[iFrom].append( iScore )
		self.m_pTos.append( iTo )
		self.m_pEs.append( dE )
		self.m_pIDs.append( dID )
		self.m_pCovs.append( dCov )

	def get_froms( self ):
		
		return len( self.m_astrFroms )
	
	def get_from( self, iFrom ):
		
		return self.m_astrFroms[iFrom]
	
	def get_to( self, iTo ):

		return self.m_astrTos[iTo]
	
	def get_tos( self ):

		return len( self.m_astrTos )

	def get_scoreto( self, iScore ):

		return self.m_pTos[iScore]

	def get_scores( self, iFrom ):

		return self.m_apScores[iFrom]
	
	def get_dic( self, iScore ):
		
		return [a[iScore] for a in (self.m_pEs, self.m_pIDs, self.m_pCovs)]
	
	def save( self, fileOut ):
		
		pickle.dump( self.m_astrFroms, fileOut, pickle.HIGHEST_PROTOCOL )
		pickle.dump( self.m_astrTos, fileOut, pickle.HIGHEST_PROTOCOL )
		pickle.dump( self.m_apScores, fileOut, pickle.HIGHEST_PROTOCOL )
		pickle.dump( self.m_pTos, fileOut, pickle.HIGHEST_PROTOCOL )
		pickle.dump( self.m_pEs, fileOut, pickle.HIGHEST_PROTOCOL )
		pickle.dump( self.m_pIDs, fileOut, pickle.HIGHEST_PROTOCOL )
		pickle.dump( self.m_pCovs, fileOut, pickle.HIGHEST_PROTOCOL )
		
	def open( self, fileIn ):
		
		self._clear( )
		self.m_astrFroms = pickle.load( fileIn )
		self.m_astrTos = pickle.load( fileIn )
		self.m_apScores = pickle.load( fileIn )
		self.m_pTos = pickle.load( fileIn )
		self.m_pEs = pickle.load( fileIn )
		self.m_pIDs = pickle.load( fileIn )
		self.m_pCovs = pickle.load( fileIn )

if __name__ == "__main__":
	pHits = CHits( )
	pHits.open( sys.stdin )
#	pHits.save( sys.stdout )
	for i in pHits.m_pTos:
		print( i )
