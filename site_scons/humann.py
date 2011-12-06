from SCons.Script import *

import glob
import os
import re
import subprocess
import sys

class CProcessor:

	def __init__( pSelf, strFrom, strTo, strID, strProcessor, astrDeps,
		astrArgs = [], fInput = False, fGzip = False ):

		pSelf.m_strSuffix = pSelf.m_strFrom = None
		if fInput:
			pSelf.m_strSuffix = strFrom
		else:
			pSelf.m_strFrom = strFrom
		pSelf.m_strTo = strTo
		pSelf.m_strID = strID
		pSelf.m_strProcessor = strProcessor
		pSelf.m_astrDeps = astrDeps
		pSelf.m_astrArgs = astrArgs
		pSelf.m_fGzip = fGzip

	def deps( pSelf ):

		return ( [pSelf.m_strProcessor] + pSelf.m_astrDeps )

	def in2out( pSelf, strIn ):

		fInput = re.search( c_strDirInput + '.*' + ( pSelf.m_strSuffix or "" ) + '$', strIn )
		if ( pSelf.m_strSuffix and not fInput ) or \
			( pSelf.m_strFrom and ( fInput or not
			re.search( '_' + pSelf.m_strFrom + '-', strIn ) ) ):
			return None

		if not fInput:
			strIn = re.sub( '\\.gz$', "", strIn )
		strIn = re.sub( '^.*' + c_strDirInput + '/', c_strDirOutput + "/",
			strIn )
		strRet = re.sub( ( pSelf.m_strSuffix + '()$' ) if pSelf.m_strSuffix else
			( '_' + pSelf.m_strFrom + '(-.*)' + c_strSuffixOutput + '$' ),
			"_" + pSelf.m_strTo + "\\1-" + pSelf.m_strID + c_strSuffixOutput, strIn )
		if pSelf.m_fGzip:
			strRet += ".gz"
		return strRet

	def out2in( pSelf, strOut ):

		if pSelf.m_fGzip:
			strOut = re.sub( '\\.gz$', "", strOut )
		if pSelf.m_strSuffix:
			strOut = re.sub( '^.*/', c_strDirInput + "/", re.sub(
				c_strSuffixOutput + '$', pSelf.m_strSuffix, strOut ) )
		strRet = re.sub( '_' + pSelf.m_strTo + '(.*)-' + pSelf.m_strID,
			( "_" + pSelf.m_strFrom + "\\1" ) if pSelf.m_strFrom else "", strOut )
		return strRet
		
	def cmd( pSelf ):
		
		return " ".join( pSelf.deps( ) + pSelf.m_astrArgs )

	def ex( pSelf ):
		
		def rn( target, source, env, pSelf = pSelf ):
		
			strCmd, strT, astrSs = cts( target, source )
			strCmd = " ".join( (strCmd, astrSs[0], "|", pSelf.cmd( )) )
			if pSelf.m_fGzip:
				strCmd += " | gzip -c"
			return ex( out( strCmd, strT ) )
			
		return rn

c_strDirData				= "data"
c_strDirSrc					= "src"
c_strDirSynth				= "synth"
c_strDirCyc					= "biocyc"

# KEGG is now defunct, and HUMAnN has been adapted accordingly using final v56
c_strURLKEGG				= "" # "ftp://ftp.genome.jp/pub/kegg/"

def data( strFile ):
	return "/".join( (c_strDirData, strFile) )
# KEGG
c_strFileMapKEGGTAB			= data( "map_title.tab" )
c_strFileKO					= data( "ko" )
c_strFileGenesPEP			= data( "genes.pep" )
c_strFileModule				= data( "module" )
# MetaCyc
c_strFileMetaCycGenes		= data( "reactions.dat" )
c_strFileMetaCycPaths		= data( "pathways.dat" )
# KEGG derived
c_strFileMapKEGGTXT			= data( "map_kegg.txt" )
c_strFileKOC				= data( "koc" )
c_strFileModuleC			= data( "modulec" )
c_strFileModuleP			= data( "modulep" )
c_strFileKEGGC				= data( "keggc" )
c_strFileGeneLs				= data( "genels" )
c_strFileTaxPC				= data( "taxpc" )
c_strFileECC				= data( "ecc" )
c_strFileCOGC				= data( "cogc" )
c_strFileKOCGZ				= data( "koc.gz" )
c_strFileGeneLsGZ			= data( "genels.gz" )
# MetaCyc derived
c_strFileMCC				= data( "mcc" )
c_strFileMCPC				= data( "mcpc" )
# Other
c_strFilePathwayC			= data( "pathwayc" )
c_strFileMPTARGZ			= data( "minpath1.2.tar.gz" )
c_strDirMP					= data( "MinPath" )

def prog( strFile ):
	return "/".join( (c_strDirSrc, strFile) )
#===============================================================================
# Pipeline scripts
#===============================================================================
c_strProgBlast2Hits			= prog( "blast2hits.py" )
c_strProgHits2Enzymes		= prog( "hits2enzymes.py" )
c_strProgHits2Metacyc		= prog( "hits2metacyc.py" )
c_strProgHits2Metarep		= prog( "hits2metarep.py" )
c_strProgTab2Enzymes		= prog( "tab2enzymes.py" )
c_strProgJGI2Enzymes		= prog( "jgi2enzymes.py" )
c_strProgJCVI2Enzymes		= prog( "jcvi2enzymes.py" )
c_strProgEnzymes2Pathways	= prog( "enzymes2pathways.py" )
c_strProgEnzymes2PathwaysMP	= prog( "enzymes2pathways_mp.py" )
c_strProgTaxlim				= prog( "taxlim.py" )
c_strProgSmoothWB			= prog( "smooth_wb.py" )
c_strProgSmooth				= prog( "smooth.py" )
c_strProgGapfill			= prog( "gapfill.py" )
c_strProgXipe				= prog( "xipe.py" )
c_strProgTrimXP				= prog( "trim_xp.py" )
c_strProgPathCov			= prog( "pathcov.py" )
c_strProgPathCovXP			= prog( "pathcov_xp.py" )
c_strProgPathAb				= prog( "pathab.py" )
c_strProgMP					= prog( "MinPath1.2hmp.py" )
c_strFileMP					= c_strDirMP + "/" + os.path.basename( c_strProgMP )
#===============================================================================
# Postprocessing scripts
#===============================================================================
c_strProgName				= prog( "postprocess_names.py" )
c_strProgZero				= prog( "zero.py" )
c_strProgFilter				= prog( "filter.py" )
c_strProgExclude			= prog( "exclude.py" )
c_strProgNormalize			= prog( "normalize.py" )
c_strProgEco				= prog( "eco.py" )
c_strProgMetadata			= prog( "metadata.py" )
#===============================================================================
# Preprocessing scripts
#===============================================================================
c_strProgTitles2Txt			= prog( "titles2txt.py" )
c_strProgKO2KOC				= prog( "ko2koc.py" )
c_strProgKO2KEGGC			= prog( "ko2keggc.py" )
c_strProgKO2COGC			= prog( "ko2cogc.py" )
c_strProgKO2ECC				= prog( "ko2ecc.py" )
c_strProgGenes2GeneLs		= prog( "genes2ls.py" )
c_strProgMetaCyc2MCC		= prog( "metacyc2mcc.py" )
c_strProgMetaCyc2MCPC		= prog( "metacyc2mcpc.py" )
c_strProgPaths2TaxPC		= prog( "paths2taxpc.py" )
c_strProgModule2ModuleC		= prog( "module2modulec.py" )
#===============================================================================
# Utility scripts
#===============================================================================
c_strProgCat				= prog( "cat.py" )
c_strProgOutput				= prog( "output.py" )
c_strProgMerge				= prog( "merge_tables.py" )
c_strProgPerf				= prog( "performance.R" )

c_strMock					= "mock"
c_strSuffixOutput			= ".txt"
c_strSuffixPerf				= ".pdf"

def ex( strCmd ):

	c_logrFileProvenanceTxt.info( strCmd )
	sys.stdout.write( "%s\n" % strCmd )
	return subprocess.call( strCmd, shell = True )

def ts( astrTargets, astrSources ):
	
	return (str(astrTargets[0]), [pF.get_abspath( ) for pF in astrSources]) 

def cts( astrTargets, astrSources ):

	strT, astrSs = ts( astrTargets, astrSources )
	strCmd = "cat"
	if astrSs[0].find( ".gz" ) >= 0:
		strCmd = "gunzip -c"
	elif astrSs[0].find( ".bz2" ) >= 0:
		strCmd = "bunzip2 -c"
	return (strCmd, strT, astrSs)

def out( strCmd, strFile ):
	
	return " ".join( (strCmd, "|", c_strProgOutput, strFile) )

def main( hashVars ):

	pE = Environment( )
	pE.Decider( "make" )
	for strVar, pVar in hashVars.items( ):
		globals( )[strVar] = pVar

	c_astrInput = []
	for pFile in Glob( c_strDirInput + "/*" ):
		strFile = str(pFile)
		for pProc in c_apProcessors:
			if ( not isexclude( strFile ) ) and pProc.in2out( strFile ):
				c_astrInput.append( strFile )
				break
	
#===============================================================================
# Utilities
#===============================================================================
	
	def rn( target, source, env ):
	
		strCmd, strT, astrSs = cts( target, source )
		return ex( out( " ".join( [strCmd, astrSs[0], "|"] + astrSs[1:] ), strT ) )
	
	def crn( strCmd ):
		
		def rn( target, source, env, strCmd = strCmd ):
		
			strCat, strT, astrSs = cts( target, source )
			return ex( out( " ".join( [strCat, astrSs[0], "|"] + [strCmd] + astrSs[1:] ), strT ) )
		return rn
	
	def download( strURL, strT ):
		
		iRet = ex( out( " ".join( ("curl", "-f", "-z", strT, "'" + strURL + "'") ), strT ) )
# 1 is curl's timestamp-ok code
# 19 is curl's document-not-found code
		return ( 0 if ( iRet in (1, 19) ) else iRet )
	
	def ret( pE, strFile ):
		
		pE.Precious( strFile )
		pE.NoClean( strFile )

#===============================================================================
# KEGG
#===============================================================================

	if c_strURLKEGG:
		def funcFileMapTitle( target, source, env ):
			strT, astrSs = ts( target, source )
			return download( c_strURLKEGG + "/pathway/map_title.tab", strT )
		pE.Command( c_strFileMapKEGGTAB, None, funcFileMapTitle )
		ret( pE, c_strFileMapKEGGTAB )
		pE.Command( c_strFileMapKEGGTXT, [c_strFileMapKEGGTAB, c_strProgTitles2Txt, c_strFileModule], rn )
		
		def funcFileModule( target, source, env ):
			strT, astrSs = ts( target, source )
			return download( c_strURLKEGG + "/module/module", strT )
		pE.Command( c_strFileModule, None, funcFileModule )
		ret( pE, c_strFileModule )
		pE.Command( c_strFileModuleC, [c_strFileModule, c_strProgModule2ModuleC], rn )
		def funcModuleP( target, source, env ):
			strCmd, strT, astrSs = cts( target, source )
			return ex( out( " ".join( [strCmd, astrSs[0], "|", astrSs[1], "1"] ), strT ) )
		pE.Command( c_strFileModuleP, [c_strFileModule, c_strProgModule2ModuleC], funcModuleP )
	
		for astrFile in ([c_strFileKO, "ko"], [c_strFileGenesPEP, "fasta/genes.pep"]):
			def funcFileKEGG( target, source, env, strPath = astrFile[1] ):
				strT, astrSs = ts( target, source )
				return download( c_strURLKEGG + "/genes/" + strPath, strT )
			pE.Command( astrFile[0], None, funcFileKEGG )
			ret( pE, astrFile[0] )
	
		for astrKO in ([c_strFileKOC, c_strProgKO2KOC], [c_strFileKEGGC, c_strProgKO2KEGGC],
			 [c_strFileCOGC, c_strProgKO2COGC], [c_strFileECC, c_strProgKO2ECC]):
			pE.Command( astrKO[0], [c_strFileKO] + astrKO[1:], rn )
		pE.Command( c_strFileKOCGZ, c_strFileKOC, crn( "gzip -c" ) )
		pE.Command( c_strFileGeneLs, [c_strFileGenesPEP, c_strProgGenes2GeneLs], rn )
		pE.Command( c_strFileGeneLsGZ, c_strFileGeneLs, crn( "gzip -c" ) )
	
		def funcTaxPC( target, source, env ):
			
			strT, astrSs = ts( target, source )
			strPattern = "*_pathway.list"
			iRet = 0
			if not glob.glob( c_strDirData + "/" + strPattern ):
				iRet = ex( "cd " + c_strDirData + " && " +
					"lftp -c mget " + c_strURLKEGG + "/genes/organisms/*/" + strPattern )
			return ( iRet or ex( out( " ".join( (astrSs[0], c_strDirData + "/" + strPattern) ),
				strT ) ) )
		pE.Command( c_strFileTaxPC, [c_strProgPaths2TaxPC], funcTaxPC )
	else:
		for (strOut, strIn) in ((c_strFileGeneLs, c_strFileGeneLsGZ), (c_strFileKOC, c_strFileKOCGZ)):
			pE.Command( strOut, strIn, crn( "cat" ) )
	
#===============================================================================
# MetaCyc
#===============================================================================

	if c_strInputMetaCyc:
		def funcFileMetaCycFile( target, source, env ):
			strT, astrSs = ts( target, source )
			strOut, strIn = os.path.basename( strT ), astrSs[0]
			strPath = c_strVersionMetaCyc + "/data/"
			return ( ex( " ".join( ("tar", "-C", c_strDirData, "-mxzf", strIn, strPath + strOut) ) ) or
				ex( "mv " + c_strDirData + "/" + strPath + strOut + " " + strT ) )
		for strFile in (c_strFileMetaCycGenes, c_strFileMetaCycPaths):
			pE.Command( strFile, c_strInputMetaCyc, funcFileMetaCycFile )
	
		for astrMC in ([c_strFileMCC, c_strFileMetaCycGenes, c_strProgMetaCyc2MCC],
			[c_strFileMCPC, c_strFileMetaCycPaths, c_strProgMetaCyc2MCPC]):
			strOut, strIn, strProg = astrMC
			pE.Command( strOut, [strIn, strProg], rn )
	
	def funcPathways( target, source, env ):
		strT, astrSs = ts( target, source )
		return ex( out( " ".join( ["cat"] + astrSs ), strT ) )
	pE.Command( c_strFilePathwayC, [c_strFileKEGGC, c_strFileModuleC] +
		( [c_strFileMCPC] if c_strInputMetaCyc else [] ), funcPathways )

#===============================================================================
# MinPath
#===============================================================================

	def funcFileMinPath( target, source, env ):
		strT, astrSs = ts( target, source )
		return download( "http://omics.informatics.indiana.edu/mg/get.php?justdoit=yes&software=" +
			os.path.basename( strT ), strT )
	pE.Command( c_strFileMPTARGZ, None, funcFileMinPath )
	ret( pE, c_strFileMPTARGZ )

	def funcFileMinPathFile( target, source, env ):
		strT, astrSs = ts( target, source )
		strIn, strProg = astrSs
		return ( ex( " ".join( ("tar", "-C", c_strDirData, "-mxzf", strIn) ) ) or
			ex( "cp " + strProg + " " + strT ) )
	pE.Command( c_strFileMP, [c_strFileMPTARGZ, c_strProgMP], funcFileMinPathFile )

#===============================================================================
# Processors
#===============================================================================
	
	astrFrom = c_astrInput
	astrTo = []
	hashTypes = {}
	while len( astrFrom ) > 0:
		astrNew = []
		for strFrom in astrFrom:
			fHit = False
			for pProc in c_apProcessors:
				strTo = pProc.in2out( strFrom )
				if strTo:
#					sys.stderr.write( "%s\n" % [strFrom, strTo, pProc.out2in( strTo )] )
					fHit = True
					astrNew.append( strTo )
					pE.Command( strTo, [strFrom] + pProc.deps( ), pProc.ex( ) )

					mtch = re.search( '.*_(\d{2})([^-]*)', strTo )
					if mtch:
						for strType in (mtch.group( 1 ), "".join( mtch.groups( ) )):
							hashTypes.setdefault( strType, set() ).add( strTo )
			if not fHit:
				astrTo.append( strFrom )
		astrFrom = astrNew
	
	hashTo = {}
	for strTo in astrTo:
		pMatch = re.search( '.*_(\d+.*?-\S+)' + c_strSuffixOutput + '$', strTo )
		if pMatch:
			hashTo.setdefault( pMatch.group( 1 ), [] ).append( strTo )

	hashPerf = {}
	for fileSynth in ( [] if ( not c_fMocks ) else \
		Glob( "/".join( (c_strDirSynth, c_strDirOutput, c_strMock + "_*_0[0-9]*" + c_strSuffixOutput) ) ) + \
		Glob( "/".join( (c_strDirSynth, c_strDirCyc, "*" + c_strMock + "_*_0[0-9]*" + c_strSuffixOutput) ) ) ):
		pMatch = re.search( '(?:([^/]+)_)?(' + c_strMock + '.*)_(\d{2}[^-.]*)', str(fileSynth) )
		if not pMatch:
			continue
		strPaths, strBase, strType = pMatch.groups( )
		astrFiles = filter( lambda s: s.find( strBase ) >= 0, hashTypes.get( strType, [] ) )
		if strPaths:
			astrFiles = filter( lambda s: s.find( strPaths ) >= 0, astrFiles )
			strBase = "_".join( (strPaths, strBase) )
		strType, strSubtype = strType[0:2], strType[2:]
		strType = strBase + "_" + strType
		strFile = c_strDirOutput + "/" + strType + strSubtype + c_strSuffixOutput
		hashTo[strType + strSubtype] = [str(fileSynth)] + astrFiles
		hashPerf.setdefault( strType, set() ).add( strFile )

	for strType, astrType in hashTo.items( ):
		strFile = c_strDirOutput + "/" + strType + c_strSuffixOutput
		aastrFinalizers = []
		setFinalizers = set()
		for astrFinalizer in c_aastrFinalizers:
			if ( not astrFinalizer[0] ) or re.search( astrFinalizer[0], strFile ):
				aastrFinalizers.append( astrFinalizer[1:] )
				if len( astrFinalizer ) > 2:
					setFinalizers |= set(astrFinalizer[2])
	
		def funcFile( target, source, env, astrFiles = astrType, aastrFinalizers = aastrFinalizers ):
	
			strT, astrSs = ts( target, source )
			strFinalizers = " | ".join( map( lambda a: " ".join( [a[0]] + ( a[1] if ( len( a ) > 1 ) else [] ) ), aastrFinalizers ) )
			if len( strFinalizers ) > 0:
				strFinalizers += " | "
			return ex( out( " ".join( [astrSs[0]] + astrFiles + ["|", strFinalizers,
				astrSs[1], astrSs[2]] ), strT ) )
	
		pFile = pE.Command( strFile, [c_strProgMerge, c_strProgName, c_strFileMapKEGGTXT] +
			map( lambda a: a[0], aastrFinalizers ) + astrType + list(setFinalizers), funcFile )
		Default( pFile )
	
#===============================================================================
# Synthetic community evaluation
#===============================================================================

	for strType, astrFiles in hashPerf.items( ):
		def funcPerf( target, source, env ):
			strT, astrSs = ts( target, source )
			strR, astrArgs = astrSs[0], astrSs[1:]
			return ex( " ".join( ["R", "--no-save", "--args", strT] + astrArgs + ["<", strR] ) )

		pFile = pE.Command( c_strDirOutput + "/" + strType + c_strSuffixPerf,
			[c_strProgPerf] + sorted( astrFiles ), funcPerf )
		Default( pFile )
