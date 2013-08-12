#!/usr/bin/env python
"""
Description: preps data on the performance of HUMAnN evaluating reads from a synthetic community, for plotting in performance.R
Program called before: Called in humann.py main( ).
Program called after: performance.R
"""

import sys
import os
import subprocess
import tempfile

if len( sys.argv ) < 4:
    raise Exception( "Usage: performance.py <performance.R> <out> <pdf/ext> <in1.txt> <in2.txt> ..." )
strPerf = sys.argv[1] # The R script for creating performance metrics.
strOut = sys.argv[2] # The location of the output file.
strOutExt = sys.argv[3] # The file extension of the output file (presumed to be pdf)
astrIn = sys.argv[4:] # File(s) being evaluated.

fOrg = False

hashhashOrgs = {}
hashHeaders = {}
for strIn in astrIn:
    line = 0
    header = ""
    for strLine in open( strIn ):
        line += 1
        astrLine = strLine.split( "\t" )
        if astrLine[0] == "ID":
            fOrg = astrLine[2] == "Organism"
        if ( line > 18 ):
            hashOrgs.setdefault( astrLine[2] if fOrg else None, {} ).setdefault( strIn, set() ).add( tuple( astrLine[0:2]  + ( [] if fOrg else [astrLine[2]] ) + astrLine[3:] ) )
        else:
            header += "\t".join( astrLine[0:2] + ( [] if fOrg else [astrLine[2]] ) + astrLine[3:] )
    hashHeaders[strIn] = header

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

        for astrLine in setLines: # Loop through all of the items in setLines. Each astrLines is one pathway/module ID with the first entry the ID alone, the second entry the ID plus the english name for the module or pathway, and the third entry is the coverage score (zero or one).

            strLine = "\t".join( astrLine ) # Join each tuple into a single tab-delimited line, of the form: ID     English name    (integer zero or 1)
            for i in astrLine[3:]:
                fZeroTest = ( ( float(i) > 0 ) or fZeroTest ) # Thus, fZeroTest and fZeroTestLine default to zero on all entries.
                fZeroTestLine = ( ( float(i) > 0 ) or fZeroTestLine )
            fNotExists = len( astrLine ) == 3
            fZeroMock = ( ( float( astrLine[2] ) > 0 ) or fZeroMock ) # Is set to true if the coverage integer is 1, sets to zero if it's 0.
            fZeroMockLine = ( ( float( astrLine[2] ) > 0 ) or fZeroMockLine )
            fZeroMismatch = ( ( fZeroMockLine and fZeroTestLine ) or fZeroMismatch )
            os.write( iTmp, strLine )
        os.close( iTmp )
        aTmpFiles.append( strTmp )

    if ( not fZeroTest ) or ( not fZeroMock ) or fNotExists or ( not fZeroMismatch ) or ( not fIn ): # If any of these conditions return true, then delete all of the files in aTmpFiles
        for strTmp in aTmpFiles: # Remove al the files from aTmpFiles.
            os.unlink( strTmp )
        continue

    print " ".join(["Rscript", strPerf, os.path.realpath( strOut 
    + ( ( "-" + strOrg ) if fOrg else "" ) + "." + strOutExt )] # Print a call to Performance.R
    + aTmpFiles)

    # Of the form Rscript Performance.R outputfilename(-org code).pdf tempfilename tempfilename
    subprocess.call( ["Rscript", strPerf, os.path.realpath( strOut 
    + ( ( "-" + strOrg ) if fOrg else "" ) + "." + strOutExt )]
    + aTmpFiles, stdout = sys.stderr)
    

    for strTmp in aTmpFiles:
        os.unlink( strTmp )
