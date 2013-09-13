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
# Example: exclude any file whose filename does not contain "example".
#		( strInput.find( "example" ) < 0 )
		)

# Directory name scanned for input files
c_strDirInput						= "input"
# Directory into which all output files are placed
c_strDirOutput						= "output"
# Filename from which metadata annotations are read; can be excluded (see below)

c_strInputMetadata					= c_strDirInput + "/hmp_metadata.dat"
# Optional: MetaCyc distribution tarball, will be used for pathways if present
c_strInputMetaCyc					= "" # c_strDirInput + "/meta.tar.gz"
c_strVersionMetaCyc					= "14.6"
# Optional: Generate synthetic community performance descriptors
# Note: Should build synthetic communities in the "synth" subdirectory first if enabled
c_fMocks							= False
# Optional: Generate results on a per-organism (rather than whole-community) basis
c_fOrg								= False

# Filename into which all processing steps are logged for provenance tracking
logging.basicConfig( filename = "provenance.txt", level = logging.INFO,
		format = '%(asctime)s %(levelname)-8s %(message)s' )
c_logrFileProvenanceTxt		 = logging.getLogger( )

c_apProcessors						= [
#===============================================================================
# Default: txt or gzipped txt blastx data
#===============================================================================
# Each input processor takes up to eight arguments:
#	The input filename extension targeted by the processor
#	The output numerical type tag (identifying the type of data; see README.text)
#	The output textual processor label (identifying the way in which the data were generated; see README.text)
#	The processing script for this input type
#	A list of zero or more additional files provided on the command line to the processing script
#	A list of zero or more non-file arguments provided on the command line to the script
#	True if the processor is for input files (and not intermediate files)
#	True if the processor's output should be gzip compressed
	CProcessor( ".txt",						"00",					"hit",	c_strProgBlast2Hits,
				[],							[],						True,	True ),
	CProcessor( ".txt.gz",					"00",					"hit",	c_strProgBlast2Hits,
				[],							[],						True,	True ),
#===============================================================================
# Default: mapped bam data
#===============================================================================
	CProcessor( ".bam",						"00",					"hit",	c_strProgBam2Hits,
				[],							[],						True,	True ),
#===============================================================================
# Default: multiple pre-quantified gene identifiers in tab-delimited text
#===============================================================================
# Note that for unfortunate technical reasons, the output directory, numerical type tag,
# and textual processor label must match the script's command line arguments as shown.  
	CProcessor( ".pcl",						"01",					"hit-keg",	c_strProgTSV2Hits,
				[],							[c_strDirOutput + "/", "_01-hit-keg" + c_strSuffixOutput],	True ),
	CProcessor( ".tsv",						"01",					"hit-keg",	c_strProgTSV2Hits,
				[],							[c_strDirOutput + "/", "_01-hit-keg" + c_strSuffixOutput],	True ),
	CProcessor( ".csv",						"01",					"hit-keg",	c_strProgTSV2Hits,
				[],							[c_strDirOutput + "/", "_01-hit-keg" + c_strSuffixOutput],	True ),
#===============================================================================
# Example: bzipped mapx data
#===============================================================================
#	CProcessor( ".mapx.bz2",				"00",					"hit",	c_strProgBlast2Hits,
#				[],							["mapx"],				True,	True ),
# Keep just the top 20 hits and nothing above 90% identity (e.g. for evaluation of the synthetic communities)
#	CProcessor( ".mapx.gz",					"00",					"htt",	c_strProgBlast2Hits,
#				[],							["mapx", "0.9", "20"],	True,	True ),
#===============================================================================
# Example: gzipped mblastx data
#===============================================================================
#	CProcessor( ".mblastx.gz",				"00",					"hit",	c_strProgBlast2Hits,
#				[],							["mblastx"],			True,   True ),
# Keep nothing above 95% identity (e.g. for evaluation of the synthetic communities)
#	CProcessor( ".mblastx.gz",				"00",					"htt",	c_strProgBlast2Hits,
#				[],							["mblastx", "0.95"],	True,	True ),

#------------------------------------------------------------------------------ 

# Each non-input processor takes up to six arguments:
#	The input numerical type tag
#	The output numerical type tag
#	The output textual processor label
#	The processing script
#	A list of zero or more files provided on the command line to the processing script
#	A list of zero or more non-file arguments provided on the command line to the script
#===============================================================================
# hits -> enzymes
#===============================================================================
# Generate KO abundances from BLAST hits
	CProcessor( "00",						"01",					"keg",	c_strProgHits2Enzymes,
				[c_strFileKOC, c_strFileGeneLs],	[str( c_fOrg )] ),
	CProcessor( "01",						"01b",					"cat",	c_strProgCat,
				[] ),
# Generate MetaCyc enzyme abundances from BLAST hits
# Enable only if c_strInputMetaCyc is defined above
#	CProcessor( "00",						"11",					"mtc",	c_strProgHits2Metacyc,
#				[c_strFileMCC] ),
#===============================================================================
# hits -> metarep
#===============================================================================
# Optional: Generate a METAREP input file from BLAST hits
#	CProcessor( "00",						"99",					"mtr",	c_strProgHits2Metarep,
#				[c_strFileGeneLs] ),
#===============================================================================
# enzymes -> pathways
#===============================================================================
# Generate KEGG pathway assignments from KOs
	CProcessor( "01",						"02a",					"mpt",	c_strProgEnzymes2PathwaysMP,
				[c_strFileMP, c_strFileKEGGC] ),
# Generate KEGG module assignments from KOs
	CProcessor( "01",						"02a",					"mpm",	c_strProgEnzymes2PathwaysMP,
				[c_strFileMP, c_strFileModuleC] ),
# Generate MetaCyc pathway assignments from enzymes
	CProcessor( "11",						"02a",					"mpt",	c_strProgEnzymes2PathwaysMP,
				[c_strFileMP, c_strFileMCPC] ),
#===============================================================================
# taxonomic provenance
#===============================================================================
	CProcessor( "02a",						"02b",					"cop",	c_strProgTaxlim,
				[c_strFileTaxPC, c_strFileKOC] ),
#===============================================================================
# smoothing
#===============================================================================
# Smoothing is disabled by default with the latest KEGG Module update
#	CProcessor( "02b",						"03a",					"wbl",	c_strProgSmoothWB,
#				[c_strFilePathwayC] ),
	CProcessor( "02b",						"03a",					"nul",	c_strProgCat,
				[] ),
#===============================================================================
# gap filling
#===============================================================================
	CProcessor( "03a",						"03b",					"nve",	c_strProgGapfill,
				[c_strFilePathwayC] ),
#===============================================================================
# COVERAGE
#===============================================================================
	CProcessor( "03b",						"03c",					"nve",	c_strProgPathCov,
				[c_strFilePathwayC, c_strFileModuleP] ),
	CProcessor( "03c",						"04a",					"xpe",	c_strProgPathCovXP,
				[c_strProgXipe] ),
#===============================================================================
# ABUNDANCE
#===============================================================================
	CProcessor( "03b",						"04b",					"nve",	c_strProgPathAb,
				[c_strFilePathwayC, c_strFileModuleP] ),
]

#===============================================================================
# A chain of piped finalizers runs on each file produced by the processing
# pipeline that is _not_ further processed; in other words, the coverage 04a and
# abundance 04b and 01b files.  Each finalizer consists of up to three parts:
#	An optional regular expression that must match filenames on which it is run
#	The processing script
#	A list of zero or more files provided on the command line to the processing script.
#===============================================================================
c_aastrFinalizers	= [
	[None,			c_strProgZero],
	[None,			c_strProgFilter,		[c_strFilePathwayC, c_strFileModuleP]],
	[r'0(1|(4b))',  c_strProgNormalize],
	[None,			c_strProgEco],
	[None,			c_strProgMetadata,		[c_strInputMetadata]],
]

#===============================================================================
# A chain of piped exporters runs on each final file produced in the previous step.
# Each exporter consists of up to three parts:
#	An optional regular expression that must match filenames on which it is run
#	An array containing:
#		The processing script
#		An array of zero or more files provided on the command line to the processing script
#	A required tag for the file to differentiate it from other HUMAnN outputs
#===============================================================================
c_aastrExport		= [
	[r'04b.*mpt',	[[c_strProgGraphlanTree, [c_strFileGraphlan]]],		"-graphlan_tree"],
	[r'04b.*mpm',   [[c_strProgGraphlanTree, [c_strFileGraphlan]]],		"-graphlan_tree"],
	[r'04b.*mpt',	[[c_strProgGraphlanRings, [c_strFileGraphlan]]],	"-graphlan_rings"],
	[r'04b.*mpm',   [[c_strProgGraphlanRings, [c_strFileGraphlan]]],	"-graphlan_rings"],
]

main( globals( ) )
