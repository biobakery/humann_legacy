from humann import *

import logging
import logging.handlers
import re

def isexclude( strInput ):

#	if re.search( 'mock[^_]', strInput ):
#		return True
#	if re.search( 'HMPZ', strInput ):
#		return True

#	mtch = re.search( '(SRS\d+)', strInput )
	return (
		False
#		( strInput.find( "338793263-700106436" ) < 0 ) and ( strInput.find( "mock" ) < 0 ) and
#		not re.search( '[a-z]-7\d+-7\d+', strInput )
#		( strInput.find( "mock_" ) < 0 ) and ( strInput.find( "SRS" ) < 0 )
#		( strInput.find( "AnteriorNares" ) < 0 ) and ( strInput.find( "508703490-700038756" ) < 0 )
#		strInput.find( "SRS" ) < 0
#		( not mtch ) or ( mtch.group( 1 ) not in set(["SRS055982", "SRS024075", "SRS064774", "SRS056323", "SRS024281", "SRS052988", "SRS065431", "SRS017156"]) )
	)

c_strDirInput				= "input"
c_strDirOutput				= "output"
c_strInputMetadata			= c_strDirInput + "/hmp_metadata.txt"

logging.basicConfig( filename = "provenance.txt", level = logging.INFO,
	format = '%(asctime)s %(levelname)-8s %(message)s' )
c_logrFileProvenanceTxt		= logging.getLogger( )

# TODO: remove mockrefs
c_strInputMockrefs			= "mockrefs/mockrefs.txt"

c_apProcessors				= [
#===============================================================================
# mapx 100 samples
#===============================================================================
	CProcessor( ".txt.bz2",			"00",	"hit",	c_strProgBlast2Hits,
		[],									["mapx"],		True,	True ),
#===============================================================================
# mapx synthetic community
#===============================================================================
# Keeping just the top 20 hits doesn't generally hurt performance
#	CProcessor( ".txt.gz",			"00",	"htt",	c_strProgBlast2Hits,
#		[],									["mapx", "0.98", "20"],		True,	True ),
# No reason to include identical hits
#	CProcessor( ".txt.gz",			"00",	"hta",	c_strProgBlast2Hits,
#		[],									["mapx", "1"],				True,	True ),
#	CProcessor( ".txt.gz",			"00",	"htb",	c_strProgBlast2Hits,
#		[],									["mapx", "0.98"],			True,	True ),
	CProcessor( ".txt.gz",			"00",	"hit",	c_strProgBlast2Hits,
		[],									["mapx"],		True,	True ),
#===============================================================================
# mblastx synthetic community
#===============================================================================
# Keeping just the top 20 hits doesn't generally hurt performance
#	CProcessor( "_mblastxv2.0.8.gz",	"00",	"htt",	c_strProgBlast2Hits,
#		[],									["mblastx", "0.9", "20"],	True,	True ),
# No reason to include identical hits
#	CProcessor( "_mblastxv2.0.8.gz",	"00",	"hta",	c_strProgBlast2Hits,
#		[],									["mblastx", "1"],			True,	True ),
#	CProcessor( "_mblastxv2.0.8.gz",	"00",	"htb",	c_strProgBlast2Hits,
#		[],									["mblastx", "0.98"],		True,	True ),
	CProcessor( "_mblastxv2.0.8.gz",	"00",	"htc",	c_strProgBlast2Hits,
		[],									["mblastx", "0.9"],			True,	True ),
	CProcessor( "_mblastxv2.0.8.gz",	"00",	"hit",	c_strProgBlast2Hits,
		[],									["mblastx"],	True,	True ),
#===============================================================================
# mapx 5 samples
#===============================================================================
	CProcessor( ".alignments.gz",	"00",	"hit",	c_strProgBlast2Hits,
		[],									["mapx"],		True,	True ),
#===============================================================================
# annotations mock communities
#===============================================================================
	CProcessor( ".tab",				"01",	"keg",	c_strProgTab2Enzymes,
		[c_strInputMockrefs],				[],				True ),
	CProcessor( ".jgi",				"01",	"keg",	c_strProgJGI2Enzymes,
		[c_strFileCOGC],					[],				True ),
	CProcessor( ".jcvi",			"01",	"keg",	c_strProgJCVI2Enzymes,
		[c_strFileECC],						[],				True ),
#===============================================================================
# HMP mblastx data
#===============================================================================
	CProcessor( ".out.gz",			"00",	"keg",	c_strProgBlast2Hits,
		[],									["mblastx"],	True,	True ),
#===============================================================================
# HMP KO + MetaCyc data
#===============================================================================
	CProcessor( "__01-keg.txt",		"02a",	"mpt",	c_strProgEnzymes2PathwaysMP,
		[c_strFileMP, c_strFileKEGGC],		[],				True ),
	CProcessor( "__01-keg.txt",		"02a",	"mpm",	c_strProgEnzymes2PathwaysMP,
		[c_strFileMP, c_strFileModuleC],	[],				True ),
	CProcessor( "__11-mtc.txt",		"02a",	"mpy",	c_strProgEnzymes2PathwaysMP,
		[c_strFileMP, c_strFileMCPC],		[],				True ),
#===============================================================================
# hits -> enzymes
#===============================================================================
	CProcessor( "00",	"01",	"keg",	c_strProgHits2Enzymes,
		[c_strFileKOC, c_strFileGeneLs] ),
	CProcessor( "00",	"11",	"mtc",	c_strProgHits2Metacyc,
		[c_strFileMCC] ),
	CProcessor( "00",	"99",	"mtr",	c_strProgHits2Metarep,
		[c_strFileGeneLs] ),
#===============================================================================
# enzymes -> pathways
#===============================================================================
# MinPath helps so much that we don't need to include naive pathway assignment
	CProcessor( "01",	"12a",	"nve",	c_strProgEnzymes2Pathways,
		[c_strFilePathwayC] ),
	CProcessor( "01",	"02a",	"mpt",	c_strProgEnzymes2PathwaysMP,
		[c_strFileMP, c_strFileKEGGC] ),
	CProcessor( "11",	"02a",	"mpt",	c_strProgEnzymes2PathwaysMP,
		[c_strFileMP, c_strFileMCPC] ),
	CProcessor( "01",	"02a",	"mpm",	c_strProgEnzymes2PathwaysMP,
		[c_strFileMP, c_strFileModuleC] ),
#===============================================================================
# taxonomic provenance
#===============================================================================
# Cutting off at median empirically outperforms one IQR below/above
# One IQR above =~ 0 (median), one IQR below =~ nul (none)
# Median sometimes fails catastrophically, worse on abundance
#	CProcessor( "02a",	"02b",	"nnd",	c_strProgTaxlim,
#		[c_strFileTaxPC],					["1", "1"] ),
#	CProcessor( "02a",	"02b",	"nne",	c_strProgTaxlim,
#		[c_strFileTaxPC],					["0", "1"] ),
# One STD above =~ 0 (mean), STD below =~ nul (none)
#	CProcessor( "02a",	"02b",	"nvd",	c_strProgTaxlim,
#		[c_strFileTaxPC],					["1"] ),
# Mean is most consistently best for abundance + coverage
# Particularly in most limited data (mblastx with <=90% ID)
#	CProcessor( "02a",	"02b",	"nve",	c_strProgTaxlim,
#		[c_strFileTaxPC],					[] ),
# Even naive taxonomic limitation substantially outperforms none
	CProcessor( "12a",	"12b",	"nul",	c_strProgCat,
		[],									["1"] ),
# Providing the KOC file allows taxonomic limitation to also adjust for the
# expected copy # of each KO based on organismal freq, which helps a good bit
	CProcessor( "02a",	"02b",	"cop",	c_strProgTaxlim,
		[c_strFileTaxPC, c_strFileKOC],		[] ),
#===============================================================================
# smoothing
#===============================================================================
# Witten-Bell doesn't actually help more than naive smoothing
#	CProcessor( "02b",	"03a",	"nve",	c_strProgSmooth,
#		[c_strFilePathwayC] ),
# No smoothing at all is terrible
	CProcessor( "12b",	"13a",	"nul",	c_strProgCat,
		[] ),
	CProcessor( "02b",	"03a",	"wbl",	c_strProgSmoothWB,
		[c_strFilePathwayC] ),
#===============================================================================
# gap filling
#===============================================================================
# No gap filling is much worse than naive gap filling
	CProcessor( "13a",	"13b",	"nul",	c_strProgCat,
		[] ),
# Average is better than median for abundance, worse for coverage
# IQRs/STDs don't really matter
#	CProcessor( "03a",	"03b",	"nae",	c_strProgGapfill,
#		[c_strFilePathwayC],			["0", "0"] ),
	CProcessor( "03a",	"03b",	"nve",	c_strProgGapfill,
		[c_strFilePathwayC] ),
#===============================================================================
# re-smoothing
#===============================================================================
# Xipe at this stage hurts performance (too many rare enzymes lost)
#	CProcessor( "03b",	"03c",	"xpe",	c_strProgTrimXP,
#		[c_strProgXipe] ),
	CProcessor( "13b",	"13c",	"nul",	c_strProgCat,
		[] ),
	CProcessor( "03b",	"03c",	"nul",	c_strProgCat,
		[] ),
#===============================================================================
# COVERAGE
#===============================================================================
# Xipe at this stage doesn't affect performance
# Mean vs. median doesn't matter but must match above
#	CProcessor( "03c",	"03d",	"nae",	c_strProgPathCov,
#		[c_strFilePathwayC],				["0"] ),
	CProcessor( "03c",	"03d",	"nve",	c_strProgPathCov,
		[c_strFilePathwayC, c_strFileModuleP] ),
	CProcessor( "03d",	"04a",	"xpe",	c_strProgPathCovXP,
		[c_strProgXipe] ),
	CProcessor( "13c",	"04a",	"nve",	c_strProgPathCov,
		[c_strFilePathwayC] ),
#===============================================================================
# ABUNDANCE
#===============================================================================
# Median is horrid compared to average
# But average of the upper half is better!
	CProcessor( "03c",	"04b",	"nve",	c_strProgPathAb,
		[c_strFilePathwayC, c_strFileModuleP] ),
	CProcessor( "13c",	"04b",	"nul",	c_strProgPathAb,
		[c_strFilePathwayC],					["\"\"", "0"] ),
]
c_aastrFinalizers			= [
	[None,			c_strProgZero],
	[None,			c_strProgFilter, 	[c_strFilePathwayC]],
	["0(1|(4b))",	c_strProgNormalize],
	[None,			c_strProgMetadata,	[c_strInputMetadata]],
]

main( globals( ) )
