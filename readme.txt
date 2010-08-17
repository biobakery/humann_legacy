NB
----
All of these files use KEGG Orthology KO identifiers for genes and KEGG Pathway identifiers for pathways.  This is for demonstration purposes only and not meant to suggest they'll be the only pathways used in production analyses!  Any traceable identifiers (MetaCyc, EC, etc.) can be used for enzymes and for the pathways in which they're contained.

See Rakefile for specific processing pipeline used to generate each file.

*_01-enzab.txt
----
Generated from raw BLAST results.
Relative enzyme abundances as calculated from BLAST results in which each read has been mapped to zero or more enzyme identifiers based on quality of match.  Total weight of each read is 1.0, distributed over all enzyme (KO) matches by quality.

*_02-enzabp.txt
----
Generated from *_01-enzab.txt.
Relative enzyme abundances distributed naively over all pathways in which the enzyme could occur.

*_03a-enzabpsm.txt
----
Generated from *_02-enzabp.txt.
Relative enzyme abundances with pathway assignments, smoothed so that no known enzyme (based on KEGG) has zero abundance.  Performed naively for this example by adding a constant value (0.1) to missing enzyme/pathway combinations.

*_03b-enzabpgf.txt
----
Generated from *_03a-enzabpsm.txt.
Relative enzyme abundances with pathway assignments, gap-filled so that enzyme/pathway combinations with surprisingly low frequency (below lower outer fence) are naively filled with the pathway mean.

*_04a-pathcov.txt
----
Generated from *_03b-enzabpgf.txt.
Naively calculated pathway coverage measure, i.e. relative confidence of each pathway being present in the sample.  Calculated for this example as fraction of enzymes in pathway at or above global median abundance.

*_04b-pathab.txt
----
Generated from *_03b-enzabpgf.txt.
Naively calculated pathway abundance measure, i.e. relative "copy number" of each pathway in the sample.  Calculated for this example as average abundance of all enzymes in the pathway.
