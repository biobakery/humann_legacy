#!/usr/bin/env python

import sys
import os
import subprocess

if len( sys.argv ) == 1:
    raise Exception( "Usage: fnaSplit.py <1.fna> <2.fna> ..." )
astrFNA = sys.argv[1:]

for strFNA in astrFNA:
	setstrFasta = set()
	astrFNASplit = strFNA.split( "." )
	currentFile = ""
	strPFasta = ""
	strFNAFolder = astrFNASplit[0]
	fFasta = True
	if not os.path.exists( strFNAFolder ):
		os.makedirs( strFNAFolder )
	for strLine in open( strFNA ):
		astrLine = strLine.rstrip( ).split( "\t" )
		if ( astrLine[0][0] == ">" ):
			fFasta = True
			astrSub = astrLine[0].split( "_" )
			if len( astrSub ) > 1:
				strFasta = strFNAFolder + "/" + strFNAFolder + "-" + astrSub[0][1:]
				if strFasta in setstrFasta:
					if strPFasta != strFasta:
						print( "Appending more to: " + strFasta )
					currentFile = open( strFasta + ".fasta", "a" )
				else:
					print( "New fasta file: " + strFasta )
					setstrFasta.add( strFasta )
					currentFile = open( strFasta + ".fasta", "w" )
				strPFasta = strFasta
			else:
				break
		else:
			fFasta = False
			astrSub = astrLine[0].split( "_" )
			if len( astrSub ) > 1:
				strFasta = strFNAFolder + "/" + strFNAFolder + "-" + astrSub[0][1:]
				if strFasta in setstrFasta:
					if strPFasta != strFasta:
						print( "Appending more to: " + strFasta )
					currentFile = open( strFasta + ".txt", "a" )
				else:
					print( "New text file: " + strFasta )
					setstrFasta.add( strFasta )
					currentFile = open( strFasta + ".txt", "w" )
				strPFasta = strFasta
			else:
				break
		currentFile.write( strLine )
	for strFasta in setstrFasta:
		if strFasta[-4:] != ".txt":
			print( "usearch6 -usearch_local " + strFasta + ".fasta -evalue 1e-5 -blast6out " + strFasta + ".txt -db /n/CHB/data/KEGG/KEGG_reduced/kegg.reduced.usearch6.udb -threads 4 -id 0.8" )
			subprocess.call( ["usearch6", "-usearch_local", strFasta + ".fasta", "-evalue", "1e-5", "-blast6out", strFasta + ".txt",
				"-db", "/n/CHB/data/KEGG/KEGG_reduced/kegg.reduced.usearch6.udb", "-threads", "4", "-id", "0.8"], stdout = sys.stderr)
			print( "gzip " + strFasta + ".fasta" )
			subprocess.call( ["gzip", strFasta + ".txt"], stdout = sys.stderr )