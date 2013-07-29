#!/usr/bin/env python
"""
Description: preps data on the performance of HUMAnN evaluating fake reads from a synthetic community, for plotting in performance.R
Program called before: Called in humann.py main( ).
Program called after: performance.R
"""

import sys
import os
import subprocess
import tempfile
import re
import logging

logging.basicConfig(filename='1example.log',level=logging.DEBUG)

if len( sys.argv ) < 4:
    raise Exception( "Usage: performance.py <performance.R> <out> <pdf/ext> <in1.txt> <in2.txt> ..." )
strPerf = sys.argv[1] # The R script for creating performance metrics.
strOut = sys.argv[2] # The location of the output file.
strOutExt = sys.argv[3] # The file extension of the output file (presumed to be pdf)
astrIn = sys.argv[4:] # File(s) being evaluated.

fOrg = False

hashhashOrgs = {}
hashHeaders = {}
for strIn in astrIn: # Loop through all of the files passed in:
    logging.debug( strIn )
    strHeader = ""
    fMetadataLine = False # Flag denotes if the current line is metadata or not.
    for strLine in open( strIn ): # Loop through the lines in the file.
        astrLine = strLine.split( "\t" ) # Split each line into columns by tabs.
        if astrLine[0] == "ID": # If the first word of the line is "ID":
            fOrg = astrLine[2] == "Organism" # And if the third word is "Organism", then set fOrg to true, denoting that this is an organism-specific file.
        if ( fMetadataLine == True ): # If the current line is past the metadata (ie it is true data)
            logging.debug( astrLine )
            hashhashOrgs.setdefault( astrLine[2] if fOrg else None, {} ).setdefault( strIn, set() ).add( tuple( astrLine[0:2]  + ( [] if fOrg else [astrLine[2]] ) + astrLine[3:] ) )
            # First setdefault() populates hashhashOrgs, mapping organism code to another dict if input is organism-specific.
            # Second setdefualt() adds a dict entry mapping the path of the input file being evaluated to a set.
            # The set consists of a tuple of all of the columns in the current line in the current file if there is organism-specificity.
            # If there is not organism specificity, then the third column is added twice.
        else: # For the header lines:
            strHeader += "\t".join( astrLine[0:2] + ( [] if fOrg else [astrLine[2]] ) + astrLine[3:] ) # The header is the entire line, unless it is NOT an organism-specific file, in which case the third column is added to the header twice.
        if ( astrLine[0] == "Richness"): # Check for the end of the header information ("Richness" appears on the first)
            fMetadataLine = True # Then the data starts on the next line.
    hashHeaders[strIn] = strHeader # Construct a dict mapping the input file path to it's header metadata from strHeader.


# hashhashOrgs.items( ) example output:
#
#     DEBUG:root:[('pmu', {'/n/home09/mpaull/humann/output/mock_even_lc_04a.txt': set([('ko05217', 'ko05217: Basal cell carcinoma', '0\n')])}), ('fnu', {'/n/home09
# /mpaull/humann/output/mock_even_lc_04a.txt': set([('ko00621', 'ko00621: Dioxin degradation', '0\n'), ('M00046', 'M00046: beta-Alanine biosynthesis, cytosine 
# / uracil => beta-alanine', '0\n'), ('M00354', 'M00354: Spliceosome, U4/U6.U5 tri-snRNP', '0\n'), ('ko04740', 'ko04740: Olfactory transduction', '0\n'), ('ko0
# 0966', 'ko00966: Glucosinolate biosynthesis', '0\n')])}), ('bma', {'/n/home09/mpaull/humann/output/mock_even_lc_04a.txt': set([('ko00904', 'ko00904: Diterpen
# oid biosynthesis', '0\n'), ('M00296', 'M00296: BER complex', '0\n')])}), ('fjo', {'/n/home09/mpaull/humann/output/mock_even_lc_04a.txt': set([('ko01040', 'ko
# 01040: Biosynthesis of unsaturated fatty acids', '1\n'), ('M00341', 'M00341: Proteasome, 19S regulatory particle (PA700)', '0\n')])}), ('pdi', {'/n/home09/mp
# aull/humann/output/mock_even_lc_04a.txt': set([('ko00053', 'ko00053: Ascorbate and aldarate metabolism', '0\n')])}), ('vpr', {'/n/home09/mpaull/humann/output
# /mock_even_lc_04a.txt': set([('M00201', 'M00201: alpha-Glucoside transport system', '0\n'), ('ko00260', 'ko00260: Glycine, serine and threonine metabolism', 
# '1\n')])}), ('eco', {'/n/home09/mpaull/humann/output/mock_even_lc_04a.txt': set([('M00165', 'M00165: Reductive pentose phosphate cycle (Calvin cycle)', '0\n'
# ), ('ko04210', 'ko04210: Apoptosis', '0\n')])}), ('pru', {'/n/home09/mpaull/humann/output/mock_even_lc_04a.txt': set([('M00105', 'M00105: Bile acid biosynthe
# sis, cholesterol => chenodeoxycholate', '0\n'), ('ko04622', 'ko04622: RIG-I-like receptor signaling pathway', '0\n')])}), ('rmu', {'/n/home09/mpaull/humann/o
# utput/mock_even_lc_04a.txt': set([('M00181', 'M00181: RNA polymerase III, eukaryotes', '0\n'), ('M00033', 'M00033: Ectoine biosynthesis', '0\n'), ('M00336', 
# 'M00336: Twin-arginine translocation (Tat) system', '0\n')])}), ('pgi', {'/n/home09/mpaull/humann/output/mock_even_lc_04a.txt': set([('M00045', 'M00045: Hist
# idine degradation, histidine => N-formiminoglutamate => glutamate', '0\n'), ('ko00471', 'ko00471: D-Glutamine and D-glutamate metabolism', '1\n')])}), ('lba'
# , {'/n/home09/mpaull/humann/output/mock_even_lc_04a.txt': set([('ko04722', 'ko04722: Neurotrophin signaling pathway', '0\n'), ('ko00830', 'ko00830: Retinol m
# etabolism', '0\n')])}), ('eel', {'/n/home09/mpaull/humann/output/mock_even_lc_04a.txt': set([('M00200', 'M00200: Sorbitol/mannitol transport system', '0\n'),
#  ('ko04145', 'ko04145: Phagosome', '0\n'), ('M00096', 'M00096: C5 isoprenoid biosynthesis, non-mevalonate pathway', '0\n')])}), ('nme', {'/n/home09/mpaull/hu
# mann/output/mock_even_lc_04a.txt': set([('ko03440', 'ko03440: Homologous recombination', '1\n'), ('ko04150', 'ko04150: mTOR signaling pathway', '0\n')])}), (
# 'lac', {'/n/home09/mpaull/humann/output/mock_even_lc_04a.txt': set([('M00123', 'M00123: Biotin biosynthesis, pimeloyl-CoA => biotin', '0\n'), ('ko00331', 'ko
# 00331: Clavulanic acid biosynthesis', '0\n'), ('ko00920', 'ko00920: Sulfur metabolism', '1\n'), ('M00051', 'M00051: Uridine monophosphate biosynthesis, gluta
# mine (+ PRPP) => UMP', '0\n')])}), ('cje', {'/n/home09/mpaull/humann/output/mock_even_lc_04a.txt': set([('ko04971', 'ko04971: Gastric acid secretion', '0\n')
# , ('M00002', 'M00002: Glycolysis, core module involving three-carbon compounds', '0\n')])}), ('sau', {'/n/home09/mpaull/humann/output/mock_even_lc_04a.txt': 
# set([('ko04670', 'ko04670: Leukocyte transendothelial migration', '0\n')])})]
 

for strOrg, hashFiles in hashhashOrgs.items( ): # strOrg is the organism, hashFiles is a dict mapping output files to a set containing KEGG IDs and english descriptions of KEGG pathways and modules.
    aTmpFiles = list()
    fZeroTest = False
    fZeroMock = False
    fNotExists = False
    fZeroMismatch = False
    fIn = True
    for strFile in astrIn: # Loop through the input files.
        if strFile not in hashFiles: # If the current input file is not the input file currently under examination from the hashhasOrgs dict:
            fIn = False # Then set the fIn flag to false.
            break # Break out of the input file loop.
        setLines = hashFiles[strFile] # setLines is a set of all the KEGG modules and pathways associated with the current file (all the information loaded from the [filename] entry of hashFiles.
        iTmp, strTmp = tempfile.mkstemp( )
        os.write( iTmp, hashHeaders[strFile] )
        fZeroTestLine = False
        fZeroMockLine = False
        #if strOrg == 'cdf':
        #    logging.debug( hashFiles[strFile] )
        for astrLine in setLines: # Loop through all of the items in setLines. Each astrLines is one pathway/module ID with the first entry the ID alone, the second entry the ID plus the english name for the module or pathway, and the third entry is the coverage score (zero or one).
            # logging.debug( "astrLine[3:] is: " )
            #logging.debug( astrLine[3:] )

            # Example astrLine with fOrg:
            # DEBUG:root:('ko00640', 'ko00640: Propanoate metabolism', '1', '0', '0\n')
            # DEBUG:root:astrLine is: 
            # DEBUG:root:('ko04745', 'ko04745: Phototransduction - fly', '0', '0', '0\n')
            # DEBUG:root:astrLine is: 
            # DEBUG:root:('M00156', 'M00156: Complex IV (Cytochrome c oxidase), cytochrome c oxidase, cbb3-type', '0', '0', '0\n')
            # DEBUG:root:astrLine is: 
            # DEBUG:root:('M00129', 'M00129: Ascorbate biosynthesis, animals, glucose-1P => ascorbate', '0', '0', '0\n')

            # Example astrLine without fOrg:
            # DEBUG:root:('M00028', 'M00028: Ornithine biosynthesis, glutamate => ornithine', '0\n')
            # DEBUG:root:('ko04270', 'ko04270: Vascular smooth muscle contraction', '0\n')


            strLine = "\t".join( astrLine ) # Join each tuple into a single tab-delimited line, of the form: ID     English name    (integer zero or 1)
            for i in astrLine[3:]: # HERE --> There is nothing beyond the third entry in astrLine.
                # No entries (with org specificity turned OFF)
                fZeroTest = ( ( float(i) > 0 ) or fZeroTest ) # Thus, fZeroTest and fZeroTestLine default to zero on all entries.
                fZeroTestLine = ( ( float(i) > 0 ) or fZeroTestLine )
            fNotExists = len( astrLine ) == 3
            fZeroMock = ( ( float( astrLine[2] ) > 0 ) or fZeroMock ) # Is set to true if the coverage integer is 1, sets to zero if it's 0.
            fZeroMockLine = ( ( float( astrLine[2] ) > 0 ) or fZeroMockLine )
            fZeroMismatch = ( ( fZeroMockLine and fZeroTestLine ) or fZeroMismatch )
            os.write( iTmp, strLine )
        os.close( iTmp )
        aTmpFiles.append( strTmp )


    LOGfZeroTest = "fZeroTest" if ( fZeroTest == False ) else ""
    LOGfZeroMock = "fZeroMock" if ( fZeroMock == False ) else ""
    LOGfNotExists = "fNotExists" if ( fNotExists == True ) else ""
    LOGfZeroMismatch = "fZeroMismatch" if ( fZeroMismatch == False ) else ""
    LOGfIn = "fIn" if ( fIn == False ) else ""

    if strOrg == 'cdf':
        logging.debug( aTmpFiles )
    logging.debug( "\n" )
    logging.debug( strFile )
    logging.debug( strOrg )
   # logging.debug( "fZeroTest is (true?): ******************************************************************************************************************************" )
    if ( LOGfZeroTest ):
        logging.debug( LOGfZeroTest )
   # logging.debug( "\n" )
   # logging.debug( "fZeroMock is (true?): ******************************************************************************************************************************" )
    if ( LOGfZeroMock ):
        logging.debug( LOGfZeroMock )
   # logging.debug( "\n" )
   # logging.debug( "fNotExists is (false?): ******************************************************************************************************************************" )
    if ( LOGfNotExists ):
        logging.debug( LOGfNotExists )
   # logging.debug( "\n" )
   # logging.debug( "fZeroMismatch is (true?): ******************************************************************************************************************************" )
    if ( LOGfZeroMismatch ):
        logging.debug( LOGfZeroMismatch )
   # logging.debug( "\n" )
   # logging.debug( "fIn is (true?): ******************************************************************************************************************************" )
    if ( LOGfIn ):
        logging.debug( LOGfIn )
   # logging.debug( "\n" )

    # if ( LOGfZeroTest ):
    #     logging.debug( strFile )



    if ( not fZeroTest ) or ( not fZeroMock ) or fNotExists or ( not fZeroMismatch ) or ( not fIn ): # If any of these conditions return true, then delete all of the files in aTmpFiles
    # Because fZeroTest defaults to zero above, this evaluation will always default to true, meaning 100% of the entries get removed from aTmpFiles
    # fZeroMismatch also always triggering this
        for strTmp in aTmpFiles: # Remove al the files from aTmpFiles.
            os.unlink( strTmp )
        continue

    #logging.debug( "aTmpFiles[0] is: ******************************************************************************************************************************" )
    #logging.debug( os.path.realpath( aTmpFiles[0] ) )
    print " ".join(["Rscript", strPerf, os.path.realpath( strOut 
    + ( ( "-" + strOrg ) if fOrg else "" ) + "." + strOutExt )] # Print a call to Performance.R
    + aTmpFiles)

    # Of the form Rscript Performance.R outputfilename(-org code).pdf tempfilename tempfilename
    subprocess.call( ["Rscript", strPerf, os.path.realpath( strOut 
    + ( ( "-" + strOrg ) if fOrg else "" ) + "." + strOutExt )]
    + aTmpFiles, stdout = sys.stderr)
    
    logging.debug( ["Rscript", strPerf, os.path.realpath( strOut 
    + ( ( "-" + strOrg ) if fOrg else "" ) + "." + strOutExt )]
    + aTmpFiles )
    logging.debug( aTmpFiles )



    # for strTmp in aTmpFiles:
    #     os.unlink( strTmp )