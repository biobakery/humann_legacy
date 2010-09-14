import logging
import logging.handlers
import re
import subprocess
import sys

def isexclude( strInput ):

	return (
		False
#		( strInput.find( "338793263-700106436" ) < 0 ) and ( strInput.find( "mock" ) < 0 ) and
#		not re.search( '[a-z]-7\d+-7\d+', strInput )
#		strInput.find( "mock" ) < 0
	)

class CProcessor:

	def __init__( pSelf, strFrom, strTo, strID, strProcessor, astrDeps,
		fInput = False ):

		pSelf.m_strSuffix = pSelf.m_strFrom = None
		if fInput:
			pSelf.m_strSuffix = strFrom
		else:
			pSelf.m_strFrom = strFrom
		pSelf.m_strTo = strTo
		pSelf.m_strID = strID
		pSelf.m_strProcessor = strProcessor
		pSelf.m_astrDeps = astrDeps

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

c_strDirInput				= "data"
c_strDirOutput				= "output"
c_strInputMapKEGG			= "map_kegg.txt"
c_strFileKO					= "ko"
c_strFileKOC				= "koc"
c_strFileCOGC				= "cogc"
c_strFileECC				= "ecc"
c_strFileKEGGC				= "keggc"
logging.basicConfig( filename = "provenance.txt", level = logging.INFO, format = '%(asctime)s %(levelname)-8s %(message)s' )
c_logrFileProvenanceTxt		= logging.getLogger( )
#c_logrFileProvenanceTxt.addHandler( logging.handlers.RotatingFileHandler( "provenance.txt" ) )
#c_logrFileProvenanceTxt.setLevel( logging.INFO )
c_strProgKO2KOC				= "./ko2koc.rb"
c_strProgKO2KEGGC			= "./ko2keggc.rb"
c_strProgKO2COGC			= "./ko2cogc.rb"
c_strProgKO2ECC				= "./ko2ecc.rb"
c_strProgMerge				= "./merge_tables.py"
c_strProgName				= "./postprocess_names.rb"
c_strProgNormalize			= "./normalize.py"
c_strSuffixOutput			= ".txt"
c_apProcessors				= [
	CProcessor( ".txt.bz2",			"01",	"keg",	"./blast2enzymes.py",
		[c_strFileKOC],		True ),
	CProcessor( ".alignments.gz",	"01",	"keg",	"./blast2enzymes.py",
		[c_strFileKOC],		True ),
#	CProcessor( ".tab",				"01",	"keg",	"./tab2enzymes.py",
#		[c_strFileKOC],		True ),
	CProcessor( ".jgi",				"01",	"keg",	"./jgi2enzymes.py",
		[c_strFileCOGC],	True ),
	CProcessor( ".jcvi",			"01",	"keg",	"./jcvi2enzymes.py",
		[c_strFileECC],		True ),
	CProcessor( "01",	"02",	"nve",	"./enzymes2pathways.py",
		[c_strFileKEGGC] ),
	CProcessor( "01",	"02",	"mpt",	"./enzymes2pathways_mp.py",
		[] ),
	CProcessor( "02",	"03a",	"nve",	"./smooth.py",
		[c_strFileKEGGC] ),
	CProcessor( "03a",	"03b",	"nve",	"./gapfill.py",
		[c_strFileKEGGC] ),
	CProcessor( "03a",	"03b",	"nul",	"./cat.py",
		[c_strFileKEGGC] ),
	CProcessor( "03b",	"04a",	"nve",	"./pathcov.py",
		[c_strFileKEGGC] ),
	CProcessor( "03b",	"04b",	"nve",	"./pathab.py",
		[c_strFileKEGGC] ),
]
c_aastrFinalizers			= [
	["04b",	"./normalize.py"],
]
c_astrInput = []
for pFile in Glob( c_strDirInput + "/*" ):
	strFile = str(pFile)
	for pProc in c_apProcessors:
		if ( not isexclude( strFile ) ) and pProc.in2out( strFile ):
			c_astrInput.append( strFile )
			break

def ex( strCmd ):

	c_logrFileProvenanceTxt.info( strCmd )
	sys.stdout.write( "%s\n" % strCmd )
	subprocess.call( strCmd, shell = True )

pE = Environment( )
pE.Decider( "timestamp-newer" )

def rn( target, source, env ):

	strT = str(target[0])
	astrSs = [pF.get_abspath( ) for pF in source]
	strCmd = "cat"
	if astrSs[0].find( ".gz" ) >= 0:
		strCmd = "z" + strCmd
	elif astrSs[0].find( ".bz2" ) >= 0:
		strCmd = "bunzip2 -c"
	ex( " ".join( [strCmd, astrSs[0], "|", astrSs[1]] + astrSs[2:] ) + " > " +
		strT )

def funcFileKO( target, source, env ):
	ex( "wget ftp://ftp.genome.jp/pub/kegg/genes/ko" )
pE.Command( c_strFileKO, None, funcFileKO )
pE.NoClean( c_strFileKO )

for astrKO in ([c_strFileKOC, c_strProgKO2KOC],
	[c_strFileKEGGC, c_strProgKO2KEGGC], [c_strFileCOGC, c_strProgKO2COGC],
	[c_strFileECC, c_strProgKO2ECC]):
	pE.Command( astrKO[0], [c_strFileKO] + astrKO[1:], rn )
	pE.NoClean( astrKO[0] )

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
				pE.Command( strTo, [strFrom] + pProc.deps( ), rn )
		if not fHit:
			astrTo.append( strFrom )
	astrFrom = astrNew

hashTo = {}
for strTo in astrTo:
	pMatch = re.search( '_(\d+.*-\S+)' + c_strSuffixOutput + '$', strTo )
	hashTo.setdefault( pMatch.group( 1 ), [] ).append( strTo )
for strType, astrType in hashTo.items( ):
	strFile = c_strDirOutput + "/" + strType + c_strSuffixOutput
	astrFinalizers = []
	for astrFinalizer in c_aastrFinalizers:
		if strFile.find( astrFinalizer[0] ) >= 0:
			astrFinalizers.append( astrFinalizer[1] )

	def funcFile( target, source, env, astrFinalizers = astrFinalizers ):

		strT = str(target[0])
		astrSs = [pF.get_abspath( ) for pF in source]
		astrFiles = astrSs[( 3 + len( astrFinalizers ) ):]
		strFinalizers = " | ".join( astrFinalizers )
		if len( astrFinalizers ) > 0:
			strFinalizers += " | "
		ex( astrSs[0] + " " + " ".join( astrFiles ) + " | " + strFinalizers +
			astrSs[1] + " " + astrSs[2] + " > " + strT )

	pE.Command( strFile, [c_strProgMerge, c_strProgName, c_strInputMapKEGG] +
		astrFinalizers + astrType, funcFile )
	Default( strFile )
