from humann import *

import logging
import logging.handlers
import re

def isexclude( strInput ):
	"""
	Given the name of an input file, return True if it should be skipped.  Useful for
	matching only a specific set (by inclusion) or removing a specific set (by exclusion)
	using regular expression patterns or raw filenames.
	"""

# Example: exclude any file whose filename ends with ".example".
#	if re.search( r'\.example$', strInput ):
#		return True

# By default, exclude nothing
	return (
		False
# Example: exclude any file not in the synthetic community MBLASTX evaluation.
#		( strInput.find( "mock_" ) < 0 ) or ( strInput.find( "vs_All" ) < 0 )
# Example: exclude any file whose filename does not contain "example".
#		( strInput.find( "example" ) < 0 )
	)

# Directory name scanned for input files
c_strDirInput				= "input"
# Directory into which all output files are placed
c_strDirOutput				= "output"
# Filename from which metadata annotations are read; can be excluded (see below)
c_strInputMetadata			= c_strDirInput + "/hmp_metadata.dat"
# Filename from which column names to remove are read; can be excluded (see below)
c_strInputExclude			= c_strDirInput + "/hmp_exclude.dat"
# Optional: MetaCyc distribution tarball, will be used for pathways if present
c_strInputMetaCyc			= c_strDirInput + "/meta.tar.gz"
c_strVersionMetaCyc			= "14.6"
# Optional: Generate synthetic community performance descriptors
# Note: Should build synthetic communities in the "synth" subdirectory if enabled
c_fMocks					= True
# Enable testing of alternative BLAST hit weighting methods (slight increases processing)
c_fWeightEval				= False
# Enable extensive parameter testing (greatly increases processing!)
c_fParameterEval			= False

# Filename into which all processing steps are logged for provenance tracking
logging.basicConfig( filename = "provenance.txt", level = logging.INFO,
	format = '%(asctime)s %(levelname)-8s %(message)s' )
c_logrFileProvenanceTxt		= logging.getLogger( )

c_apProcessors				= [
# Each input processor takes up to eight arguments:
#   The input filename extension
#   The output numerical type tag (identifying the type of data; see readme.txt)
#   The output textual processor label (identifying the way in which the data were generated; see readme.txt)
#   The processing script
#   A list of zero or more files provided on the command line to the processing script
#   A list of zero or more non-file arguments provided on the command line to the script
#   True if the processor is for input files (and not intermediate files)
#   True if the processor's output should be gzip compressed
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
#	CProcessor( "_mblastxv2.0.8.gz",	"00",	"hit",	c_strProgBlast2Hits,
#		[],									["mblastx"],	True,	True ),
#===============================================================================
# mapx 5 samples
#===============================================================================
	CProcessor( ".alignments.gz",	"00",	"hit",	c_strProgBlast2Hits,
		[],									["mapx"],		True,	True ),
#===============================================================================
# annotations mock communities
#===============================================================================
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
#	CProcessor( "__11-mtc.txt",		"02a",	"mpy",	c_strProgEnzymes2PathwaysMP,
#		[c_strFileMP, c_strFileMCPC],		[],				True ),

#------------------------------------------------------------------------------ 

# Each non-input processor takes up to six arguments:
#   The input numerical type tag
#   The output numerical type tag
#   The output textual processor label
#   The processing script
#   A list of zero or more files provided on the command line to the processing script
#   A list of zero or more non-file arguments provided on the command line to the script
#===============================================================================
# hits -> enzymes
#===============================================================================
	CProcessor( "00",	"01",	"keg",	c_strProgHits2Enzymes,
		[c_strFileKOC, c_strFileGeneLs] ),
	CProcessor( "00",	"01n",	"nve",	c_strProgHits2Enzymes,
		[c_strFileKOC, c_strFileGeneLs],	["1"] ),
	] + ( [
	CProcessor( "00",	"01",	"ksb",	c_strProgHits2Enzymes,
		[c_strFileKOC, c_strFileGeneLs],	["20", "bitscore"] ),
	CProcessor( "00",	"01",	"kie",	c_strProgHits2Enzymes,
		[c_strFileKOC, c_strFileGeneLs],	["20", "inve"] ),
	CProcessor( "00",	"01",	"ksg",	c_strProgHits2Enzymes,
		[c_strFileKOC, c_strFileGeneLs],	["20", "sigmoid"] ),
	] if c_fWeightEval else [] ) + [
#	CProcessor( "00",	"11",	"mtc",	c_strProgHits2Metacyc,
#		[c_strFileMCC] ),
#===============================================================================
# hits -> metarep
#===============================================================================
# Generate a METAREP input file from BLAST hits
#	CProcessor( "00",	"99",	"mtr",	c_strProgHits2Metarep,
#		[c_strFileGeneLs] ),
#===============================================================================
# enzymes -> pathways
#===============================================================================
# MinPath helps so much that we don't need to include naive pathway assignment
	CProcessor( "01n",	"02an",	"nve",	c_strProgEnzymes2Pathways,
		[c_strFilePathwayC] ),
	] + ( [
	CProcessor( "01",	"02a",	"nve",	c_strProgEnzymes2Pathways,
		[c_strFilePathwayC] ),
	] if c_fParameterEval else [] ) + [
	CProcessor( "01",	"02a",	"mpt",	c_strProgEnzymes2PathwaysMP,
		[c_strFileMP, c_strFileKEGGC] ),
#	CProcessor( "11",	"02a",	"mpt",	c_strProgEnzymes2PathwaysMP,
#		[c_strFileMP, c_strFileMCPC] ),
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
	] + ( [
	CProcessor( "02a",	"02b",	"nve",	c_strProgTaxlim,
		[c_strFileTaxPC],					[] ),
	] if c_fParameterEval else [] ) + [
# Even naive taxonomic limitation substantially outperforms none
	CProcessor( "02an",	"02bn",	"nul",	c_strProgCat,
		[],									["1"] ),
	] + ( [
	CProcessor( "02a",	"02b",	"nul",	c_strProgCat,
		[],									["1"] ),
	] if c_fParameterEval else [] ) + [
# Providing the KOC file allows taxonomic limitation to also adjust for the
# expected copy # of each KO based on organismal freq, which helps a good bit
	CProcessor( "02a",	"02b",	"cop",	c_strProgTaxlim,
		[c_strFileTaxPC, c_strFileKOC],		[] ),
#===============================================================================
# smoothing
#===============================================================================
# Witten-Bell doesn't actually help more than naive smoothing
	] + ( [
	CProcessor( "02b",	"03a",	"nve",	c_strProgSmooth,
		[c_strFilePathwayC] ),
	] if c_fParameterEval else [] ) + [
# No smoothing at all seems to work better with the new KEGG modules
	] + ( [
	CProcessor( "02b",	"03a",	"wbl",	c_strProgSmoothWB,
		[c_strFilePathwayC] ),
	] if c_fParameterEval else [] ) + [
	CProcessor( "02bn",	"03an",	"nul",	c_strProgCat,
		[] ),
	CProcessor( "02b",	"03a",	"nul",	c_strProgCat,
		[] ),
#===============================================================================
# gap filling
#===============================================================================
# No gap filling is much worse than naive gap filling
	CProcessor( "03an",	"03bn",	"nul",	c_strProgCat,
		[] ),
	] + ( [
	CProcessor( "03a",	"03b",	"nul",	c_strProgCat,
		[] ),
	] if c_fParameterEval else [] ) + [
# Average is better than median for abundance, worse for coverage
# IQRs/STDs don't really matter
	] + ( [
	CProcessor( "03a",	"03b",	"nae",	c_strProgGapfill,
		[c_strFilePathwayC],				["0", "0"] ),
	] if c_fParameterEval else [] ) + [
	CProcessor( "03a",	"03b",	"nve",	c_strProgGapfill,
		[c_strFilePathwayC] ),
#===============================================================================
# re-smoothing
#===============================================================================
# Xipe at this stage hurts performance (too many rare enzymes lost)
#	CProcessor( "03b",	"03c",	"xpe",	c_strProgTrimXP,
#		[c_strProgXipe] ),
	CProcessor( "03bn",	"03cn",	"nul",	c_strProgCat,
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
	CProcessor( "03cn",	"04a",	"nve",	c_strProgPathCov,
		[c_strFilePathwayC] ),
#===============================================================================
# ABUNDANCE
#===============================================================================
# Median is horrid compared to average
# But average of the upper half is better!
	CProcessor( "03c",	"04b",	"nve",	c_strProgPathAb,
		[c_strFilePathwayC, c_strFileModuleP] ),
	CProcessor( "03cn",	"04b",	"nul",	c_strProgPathAb,
		[c_strFilePathwayC],				["\"\"", "0"] ),
]

#===============================================================================
# A chain of piped finalizers runs on each file produced by the processing
# pipeline that is _not_ further processed; in other words, the coverage 04a and
# abundance 04b files.  Each finalizer consists of up to three parts:
#   An optional regular expression that must match filenames on which it is run
#   The processing script
#   A list of zero or more files provided on the command line to the processing script
#===============================================================================
c_aastrFinalizers			= [
	[None,			c_strProgZero],
	[None,			c_strProgFilter, 	[c_strFilePathwayC]],
	[None,			c_strProgExclude,	[c_strInputExclude]],
	["0(1|(4b))",	c_strProgNormalize],
	[None,			c_strProgEco],
	[None,			c_strProgMetadata,	[c_strInputMetadata]],
]

main( globals( ) )
