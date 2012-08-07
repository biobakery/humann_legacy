#!/usr/bin/env python

import sys
import os
import subprocess
import tempfile

if len( sys.argv ) < 4:
    raise Exception( "Usage: performance.py <performance.R> <out> <pdf/ext> <in1.txt> <in2.txt> ..." )
strPerf = sys.argv[1]
strOut = sys.argv[2]
strOutExt = sys.argv[3]
astrIn = sys.argv[4:]

fOrg = False

hashOrgs = {}
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
for strOrg, hashFiles in hashOrgs.items( ):
    aTmpFiles = list()
    fZeroTest = False
    fZeroMock = False
    fNotExists = False
    fZeroMismatch = False
    fIn = True
    for strFile in astrIn:
        if strFile not in hashFiles:
            fIn = False
            break
        setLines = hashFiles[strFile]
        iTmp, strTmp = tempfile.mkstemp( )
        os.write( iTmp, hashHeaders[strFile] )
        fZeroTestLine = False
        fZeroMockLine = False
        for astrLine in setLines:
            strLine = "\t".join( astrLine )
            for i in astrLine[3:]:
                fZeroTest = ( ( float(i) > 0 ) or fZeroTest )
                fZeroTestLine = ( ( float(i) > 0 ) or fZeroTestLine )
            fNotExists = len( astrLine ) == 3
            fZeroMock = ( ( float( astrLine[2] ) > 0 ) or fZeroMock )
            fZeroMockLine = ( ( float( astrLine[2] ) > 0 ) or fZeroMockLine )
            fZeroMismatch = ( ( fZeroMockLine and fZeroTestLine ) or fZeroMismatch )
            os.write( iTmp, strLine )
        os.close( iTmp )
        aTmpFiles.append( strTmp )
    if ( not fZeroTest ) or ( not fZeroMock ) or fNotExists or ( not fZeroMismatch ) or not fIn:
        for strTmp in aTmpFiles:
            os.unlink( strTmp )
        continue
    print " ".join(["Rscript", strPerf, os.path.realpath( strOut 
    + ( ( "-" + strOrg ) if fOrg else "" ) + "." + strOutExt )]
    + aTmpFiles)
    subprocess.call( ["Rscript", strPerf, os.path.realpath( strOut 
    + ( ( "-" + strOrg ) if fOrg else "" ) + "." + strOutExt )]
    + aTmpFiles, stdout = sys.stderr)
    
    for strTmp in aTmpFiles:
        os.unlink( strTmp )
