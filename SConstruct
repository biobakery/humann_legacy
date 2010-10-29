import logging
import logging.handlers
import os
import re
import subprocess
import sys

def isexclude( strInput ):

#	if re.search( 'mock[^_]', strInput ):
#		return True
#	if re.search( 'HMPZ', strInput ):
#		return True

	return (
		False
#		( strInput.find( "338793263-700106436" ) < 0 ) and ( strInput.find( "mock" ) < 0 ) and
#		not re.search( '[a-z]-7\d+-7\d+', strInput )
#		strInput.find( "mock_" ) < 0
	)

class CProcessor:

	def __init__( pSelf, strFrom, strTo, strID, strProcessor, astrDeps,
		astrArgs = [], fInput = False ):

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

	def deps( pSelf ):

		return ( [pSelf.m_strProcessor] + pSelf.m_astrDeps )

	def in2out( pSelf, strIn ):

		if ( pSelf.m_strSuffix and not re.search( c_strDirInput + '.*' +
			pSelf.m_strSuffix + '$', strIn ) ) or \
			( pSelf.m_strFrom and not re.search( '_' + pSelf.m_strFrom + '-',
			strIn ) ):
			return None

		strIn = re.sub( '^.*' + c_strDirInput + '/', c_strDirOutput + "/",
			strIn )
		return re.sub( ( pSelf.m_strSuffix + '()$' ) if pSelf.m_strSuffix else
			( '_' + pSelf.m_strFrom + '(-.*)' + c_strSuffixOutput + '$' ),
			"_" + pSelf.m_strTo + "\\1-" + pSelf.m_strID + c_strSuffixOutput,
			strIn )

	def out2in( pSelf, strOut ):

		if pSelf.m_strSuffix:
			strOut = re.sub( '^.*/', c_strDirInput + "/", re.sub(
				c_strSuffixOutput + '$', pSelf.m_strSuffix, strOut ) )
		return re.sub( '_' + pSelf.m_strTo + '(.*)-' + pSelf.m_strID,
			( "_" + pSelf.m_strFrom + "\\1" ) if pSelf.m_strFrom else "",
			strOut )
		
	def cmd( pSelf ):
		
		return " ".join( pSelf.deps( ) + pSelf.m_astrArgs )

	def ex( pSelf ):
		
		def rn( target, source, env, pSelf = pSelf ):
		
			strCmd, strT, astrSs = cts( target, source )
			return ex( out( " ".join( (strCmd, astrSs[0], "|", pSelf.cmd( )) ),
				strT ) )
			
		return rn

c_strDirInput				= "data"
c_strDirOutput				= "output"
c_strDirSynth				= "synth"
c_strInputMapKEGG			= "map_kegg.txt"
c_strInputMockrefs			= "mockrefs/mockrefs.txt"
c_strFileKO					= "ko"
c_strFileGenesPEP			= "genes.pep"
c_strFileMetaCyc			= "meta.tar.gz"
c_strFileMetaCycGenes		= "uniprot-seq-ids.dat"
c_strFileMetaCycPaths		= "pathways.dat"
c_strFileKOC				= "koc"
c_strFileMCC				= "mcc"
c_strFileMCPC				= "mcpc"
c_strFileCOGC				= "cogc"
c_strFileECC				= "ecc"
c_strFileKEGGC				= "keggc"
c_strFileGeneLs				= "genels"
c_strFilePathwayC			= "pathwayc"
c_strFileTaxPC				= "taxpc"
logging.basicConfig( filename = "provenance.txt", level = logging.INFO,
	format = '%(asctime)s %(levelname)-8s %(message)s' )
c_logrFileProvenanceTxt		= logging.getLogger( )
c_strProgKO2KOC				= "./ko2koc.py"
c_strProgKO2KEGGC			= "./ko2keggc.py"
c_strProgKO2COGC			= "./ko2cogc.py"
c_strProgKO2ECC				= "./ko2ecc.py"
c_strProgGenes2GeneLs		= "./genes2ls.py"
c_strProgMetaCyc2MCC		= "./metacyc2mcc.py"
c_strProgMetaCyc2MCPC		= "./metacyc2mcpc.py"
c_strProgMerge				= "./merge_tables.py"
c_strProgName				= "./postprocess_names.py"
c_strProgNormalize			= "./normalize.py"
c_strProgZero				= "./zero.py"
c_strProgOutput				= "./output.py"
c_strProgPaths2TaxPC		= "./paths2taxpc.py"
c_strSuffixOutput			= ".txt"
c_strMock					= "mock"
c_apProcessors				= [
#===============================================================================
# mapx 100 samples
#===============================================================================
	CProcessor( ".txt.bz2",			"01",	"keg",	"./blast2enzymes.py",
		[c_strFileKOC, c_strFileGeneLs],	[],			True ),
	CProcessor( ".txt.bz2",			"11",	"mtc",	"./blast2metacyc.py",
		[c_strFileMCC],						[],			True ),
#===============================================================================
# mapx synthetic community
#===============================================================================
# No reason to include identical hits
#	CProcessor( ".txt.gz",			"01",	"keg",	"./blast2enzymes.py",
#		[c_strFileKOC, c_strFileGeneLs],	[],			True ),
# Keeping just the top 20 hits doesn't generally hurt performance
#	CProcessor( ".txt.gz",			"01",	"ktt",	"./blast2enzymes.py",
#		[c_strFileKOC, c_strFileGeneLs],	["0.98", "0", "20"],	True ),
	CProcessor( ".txt.gz",			"01",	"kna",	"./blast2enzymes.py",
		[c_strFileKOC, c_strFileGeneLs],	["1"],		True ),
	CProcessor( ".txt.gz",			"01",	"knb",	"./blast2enzymes.py",
		[c_strFileKOC, c_strFileGeneLs],	["0.98"],	True ),
	CProcessor( ".txt.gz",			"01",	"knc",	"./blast2enzymes.py",
		[c_strFileKOC, c_strFileGeneLs],	["0.9"],	True ),
	CProcessor( ".txt.gz",			"11",	"mtc",	"./blast2metacyc.py",
		[c_strFileMCC],						[],			True ),
#===============================================================================
# mblastx synthetic community
#===============================================================================
# No reason to include identical hits
#	CProcessor( "_mblastxv2.0.8.gz",	"01",	"keg",	"./blast2enzymes.py",
#		[c_strFileKOC, c_strFileGeneLs],	["0", "1"],	True ),
# Keeping just the top 20 hits doesn't generally hurt performance
#	CProcessor( "_mblastxv2.0.8.gz",	"01",	"ktt",	"./blast2enzymes.py",
#		[c_strFileKOC, c_strFileGeneLs],	["0.98", "1", "20"],	True ),
	CProcessor( "_mblastxv2.0.8.gz",	"01",	"kna",	"./blast2enzymes.py",
		[c_strFileKOC, c_strFileGeneLs],	["1", "1"],				True ),
	CProcessor( "_mblastxv2.0.8.gz",	"01",	"knb",	"./blast2enzymes.py",
		[c_strFileKOC, c_strFileGeneLs],	["0.98", "1"],			True ),
	CProcessor( "_mblastxv2.0.8.gz",	"01",	"knc",	"./blast2enzymes.py",
		[c_strFileKOC, c_strFileGeneLs],	["0.9", "1"],			True ),
	CProcessor( "_mblastxv2.0.8.gz",	"11",	"mtc",	"./blast2metacyc.py",
		[c_strFileMCC],						["0", "1"],				True ),
#===============================================================================
# mapx 5 samples
#===============================================================================
	CProcessor( ".alignments.gz",	"01",	"keg",	"./blast2enzymes.py",
		[c_strFileKOC, c_strFileGeneLs],	[],			True ),
	CProcessor( ".alignments.gz",	"11",	"mtc",	"./blast2metacyc.py",
		[c_strFileMCC],						[],			True ),
#===============================================================================
# annotations mock communities
#===============================================================================
	CProcessor( ".tab",				"01",	"keg",	"./tab2enzymes.py",
		[c_strInputMockrefs],				[],			True ),
	CProcessor( ".jgi",				"01",	"keg",	"./jgi2enzymes.py",
		[c_strFileCOGC],					[],			True ),
	CProcessor( ".jcvi",			"01",	"keg",	"./jcvi2enzymes.py",
		[c_strFileECC],						[],			True ),
#===============================================================================
# enzymes -> pathways
#===============================================================================
# MinPath helps so much that we don't need to include naive pathway assignment
#	CProcessor( "01",	"02a",	"nve",	"./enzymes2pathways.py",
#		[c_strFilePathwayC] ),
#	CProcessor( "11",	"02a",	"nve",	"./enzymes2pathways.py",
#		[c_strFilePathwayC] ),
	CProcessor( "01",	"02a",	"mpt",	"./enzymes2pathways_mp.py",
		[c_strFileKEGGC] ),
	CProcessor( "11",	"02a",	"mpt",	"./enzymes2pathways_mp.py",
		[c_strFileMCPC] ),
#===============================================================================
# taxonomic provenance
#===============================================================================
# Cutting off at median empirically outperforms one IQR below/above
# One IQR above =~ 0 (median), one IQR below =~ nul (none)
# Median sometimes fails catastrophically, worse on abundance
#	CProcessor( "02a",	"02b",	"nnd",	"./taxlim.py",
#		[c_strFileTaxPC],					["1", "1"] ),
#	CProcessor( "02a",	"02b",	"nne",	"./taxlim.py",
#		[c_strFileTaxPC],					["0", "1"] ),
# One STD above =~ 0 (mean), STD below =~ nul (none)
#	CProcessor( "02a",	"02b",	"nvd",	"./taxlim.py",
#		[c_strFileTaxPC],					["1"] ),
# Even naive taxonomic limitation substantially outperforms none
#	CProcessor( "02a",	"02b",	"nul",	"./cat.py",
#		[],									[] ),
# Mean is most consistently best for abundance + coverage
# Particularly in most limited data (mblastx with <=90% ID)
	CProcessor( "02a",	"02b",	"nve",	"./taxlim.py",
		[c_strFileTaxPC],					[] ),
#===============================================================================
# smoothing
#===============================================================================
# Witten-Bell doesn't actually help more than naive smoothing
#	CProcessor( "02b",	"03a",	"nve",	"./smooth.py",
#		[c_strFilePathwayC] ),
# No smoothing at all is terrible
#	CProcessor( "02b",	"03a",	"nul",	"./cat.py",
#		[] ),
	CProcessor( "02b",	"03a",	"wbl",	"./smooth_wb.py",
		[c_strFilePathwayC] ),
#===============================================================================
# gap filling
#===============================================================================
# No gap filling is much worse than naive gap filling
#	CProcessor( "03a",	"03b",	"nul",	"./cat.py",
#		[] ),
# Average is better than median for abundance, worse for coverage
# IQRs/STDs don't really matter
#	CProcessor( "03a",	"03b",	"nae",	"./gapfill.py",
#		[c_strFilePathwayC],			["0", "0"] ),
	CProcessor( "03a",	"03b",	"nve",	"./gapfill.py",
		[c_strFilePathwayC] ),
#===============================================================================
# re-smoothing
#===============================================================================
# Xipe at this stage hurts performance (too many rare enzymes lost)
#	CProcessor( "03b",	"03c",	"xpe",	"./trim_xp.py",
#		[] ),
	CProcessor( "03b",	"03c",	"nul",	"./cat.py",
		[] ),
#===============================================================================
# COVERAGE
#===============================================================================
# Xipe at this stage doesn't affect performance
#	CProcessor( "03c",	"04a",	"nul",	"./cat.py",
#		[] ),
# Mean vs. median doesn't matter but must match above
#	CProcessor( "03c",	"03d",	"nae",	"./pathcov.py",
#		[c_strFilePathwayC],				["0"] ),
	CProcessor( "03c",	"03d",	"nve",	"./pathcov.py",
		[c_strFilePathwayC] ),
	CProcessor( "03d",	"04a",	"xpe",	"./pathcov_xp.py",
		[] ),
#===============================================================================
# ABUNDANCE
#===============================================================================
# Median is horrid compared to average
# But average of the upper half is better!
#	CProcessor( "03c",	"04b",	"nvm",	"./pathab.py",
#		[c_strFilePathwayC],				["0"] ),
	CProcessor( "03c",	"04b",	"nve",	"./pathab.py",
		[c_strFilePathwayC] ),
]
c_aastrFinalizers			= [
	["04a",	c_strProgZero],
	["04b",	c_strProgZero],
	["04b",	c_strProgNormalize],
	[None,	"./convenience_bsites.py"],
]
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
		strCmd = "z" + strCmd
	elif astrSs[0].find( ".bz2" ) >= 0:
		strCmd = "bunzip2 -c"
	return (strCmd, strT, astrSs)

def rn( target, source, env ):

	strCmd, strT, astrSs = cts( target, source )
	return ex( out( " ".join( [strCmd, astrSs[0], "|"] +  astrSs[1:] ), strT ) )

def out( strCmd, strFile ):
	
	return " ".join( (strCmd, "|", c_strProgOutput, strFile) )

pE = Environment( )
pE.Decider( "make" )

#===============================================================================
# KEGG
#===============================================================================

for astrFile in ([c_strFileKO, "ko"], [c_strFileGenesPEP, "fasta/genes.pep"]):
	def funcFileKEGG( target, source, env, strPath = astrFile[1] ):
		return ex( "wget -N ftp://ftp.genome.jp/pub/kegg/genes/" + strPath )
	pE.Command( astrFile[0], None, funcFileKEGG )
	pE.NoClean( astrFile[0] )

for astrKO in ([c_strFileKOC, c_strProgKO2KOC], [c_strFileKEGGC, c_strProgKO2KEGGC],
	[c_strFileCOGC, c_strProgKO2COGC], [c_strFileECC, c_strProgKO2ECC]):
	pE.Command( astrKO[0], [c_strFileKO] + astrKO[1:], rn )
	pE.NoClean( astrKO[0] )
pE.Command( c_strFileGeneLs, [c_strFileGenesPEP, c_strProgGenes2GeneLs], rn )
pE.NoClean( c_strFileGeneLs )

def funcTaxPC( target, source, env ):
	
	strT, astrSs = ts( target, source )
	strPattern = "*_pathway.list"
	iRet = 0 and ex( "cd " + c_strDirOutput + " && " +
		"lftp -c mget ftp://ftp.genome.jp/pub/kegg/genes/organisms/*/" + strPattern )
	return ( iRet or ex( out( " ".join( (astrSs[0], c_strDirOutput + "/" + strPattern) ),
		strT ) ) )
pE.Command( c_strFileTaxPC, [c_strProgPaths2TaxPC], funcTaxPC )
pE.NoClean( c_strFileTaxPC )

#===============================================================================
# MetaCyc
#===============================================================================

def funcFileMetaCyc( target, source, env ):
	strT, astrSs = ts( target, source )
	return ex( "wget -N http://brg.ai.sri.com/ecocyc/dist/flatfiles-52983746/" +
		os.path.basename( strT ) )
pE.Command( c_strFileMetaCyc, None, funcFileMetaCyc )
pE.NoClean( c_strFileMetaCyc )
def funcFileMetaCycFile( target, source, env ):
	strT, astrSs = ts( target, source )
	strOut, strIn = os.path.basename( strT ), astrSs[0]
	strPath = "14.5/data/"
	return ( ex( "tar -mxzf " + strIn + " " + strPath + strOut ) or
		ex( "mv " + strPath + strOut + " " + strT ) )
for strFile in (c_strFileMetaCycGenes, c_strFileMetaCycPaths):
	pE.Command( strFile, [c_strFileMetaCyc], funcFileMetaCycFile )
	pE.NoClean( strFile )

for astrMC in ([c_strFileMCC, c_strFileMetaCycGenes, c_strProgMetaCyc2MCC],
	[c_strFileMCPC, c_strFileMetaCycPaths, c_strProgMetaCyc2MCPC]):
	strOut, strIn, strProg = astrMC
	pE.Command( strOut, [strIn, strProg], rn )
	pE.NoClean( strOut )

def funcPathways( target, source, env ):
	strT, astrSs = ts( target, source )
	return ex( out( " ".join( ["cat"] + astrSs ), strT ) )
pE.Command( c_strFilePathwayC, [c_strFileKEGGC, c_strFileMCPC], funcPathways )
pE.NoClean( c_strFilePathwayC )

#===============================================================================
# Processors
#===============================================================================

astrFrom = c_astrInput
astrTo = []
while len( astrFrom ) > 0:
	astrNew = []
	for strFrom in astrFrom:
		fHit = False
		for pProc in c_apProcessors:
			strTo = pProc.in2out( strFrom )
			if strTo:
#				sys.stderr.write( "%s\n" % [strFrom, strTo, pProc.out2in( strTo )] )
				fHit = True
				astrNew.append( strTo )
				pE.Command( strTo, [strFrom] + pProc.deps( ), pProc.ex( ) )
		if not fHit:
			astrTo.append( strFrom )
	astrFrom = astrNew

hashTo = {}
for strTo in astrTo:
	pMatch = re.search( '_(\d+.*-\S+)' + c_strSuffixOutput + '$', strTo )
	hashTo.setdefault( pMatch.group( 1 ), [] ).append( strTo )
hashTypes = {}
for strType, astrType in hashTo.items( ):
	strFile = c_strDirOutput + "/" + strType + c_strSuffixOutput
	astrFinalizers = []
	for astrFinalizer in c_aastrFinalizers:
		if ( not astrFinalizer[0] ) or ( strFile.find( astrFinalizer[0] ) >= 0 ):
			astrFinalizers.append( astrFinalizer[1] )

	def funcFile( target, source, env, astrFinalizers = astrFinalizers ):

		strT, astrSs = ts( target, source )
		astrFiles = astrSs[( 3 + len( astrFinalizers ) ):]
		strFinalizers = " | ".join( astrFinalizers )
		if len( astrFinalizers ) > 0:
			strFinalizers += " | "
		return ex( out( " ".join( [astrSs[0]] + astrFiles + ["|", strFinalizers,
			astrSs[1], astrSs[2]] ), strT ) )

	pFile = pE.Command( strFile, [c_strProgMerge, c_strProgName, c_strInputMapKEGG] +
		astrFinalizers + astrType, funcFile )
	Default( pFile )
	
	pMatch = re.search( '(\d{2}[^-]*)', strFile )
	if pMatch:
		hashTypes.setdefault( pMatch.group( 1 ), set() ).update( astrType )

#===============================================================================
# Synthetic community evaluation
#===============================================================================

for fileSynth in Glob( "/".join( (c_strDirSynth, c_strDirOutput, c_strMock + "_*_04*" +
	c_strSuffixOutput) ) ):
	pMatch = re.search( '(' + c_strMock + '.*)_(\d{2}[^-.]*)', str(fileSynth) )
	if pMatch:
		strBase, strType = pMatch.groups( )
		astrFiles = filter( lambda strCur: strCur.find( strBase ) >= 0, hashTypes.get( strType, [] ) )
		astrProgs = [c_strProgZero]
		if strType[-1] == "b":
			astrProgs.append( c_strProgNormalize )

		def funcMock( target, source, env, astrProgs = astrProgs, astrFiles = [str(fileSynth)] + astrFiles ):
		
			strT, astrSs = ts( target, source )
			strProg = astrSs[0]
			return ex( out( " ".join( [strProg] + astrFiles + ["|",
				" | ".join( astrProgs )] ), strT ) )

		pFile = pE.Command( c_strDirOutput + "/" + strBase + "_" + strType + c_strSuffixOutput,
			[c_strProgMerge] + astrProgs + [fileSynth] + astrFiles, funcMock )
		Default( pFile )
