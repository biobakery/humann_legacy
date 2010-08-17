NB
----
All of these files use KEGG Orthology KO identifiers for genes and KEGG Pathway identifiers for pathways.  This is for demonstration purposes only and not meant to suggest they'll be the only pathways used in production analyses!  Any traceable identifiers (MetaCyc, EC, etc.) can be used for enzymes and for the pathways in which they're contained.

See Rakefile for specific processing pipeline used to generate each file.

data_01_enzab.txt
----
Generated from raw BLAST results.
Relative enzyme abundances as calculated from BLAST results in which each read has been mapped to zero or more enzyme identifiers based on quality of match.  Total weight of each read is 1.0, distributed over all enzyme (KO) matches by quality.

data_02_enzabp.txt
----
Generated from data_01_enzab.txt.
Relative enzyme abundances distributed naively over all pathways in which the enzyme could occur.

data_03a_enzabpsm.txt
----
Generated from data_02_enzabp.txt.
Relative enzyme abundances with pathway assignments, smoothed so that no known enzyme (based on KEGG) has zero abundance.  Performed naively for this example by adding a constant value (0.1) to missing enzyme/pathway combinations.

data_03b_enzabpgf.txt
----
Generated from data_03a_enzabpsm.txt.
Relative enzyme abundances with pathway assignments, gap-filled so that enzyme/pathway combinations with surprisingly low frequency (below lower outer fence) are naively filled with the pathway mean.

data_04a_pathcov.txt
----
Generated from data_03b_enzabpgf.txt.
Naively calculated pathway coverage measure, i.e. relative confidence of each pathway being present in the sample.  Calculated for this example as fraction of enzymes in pathway at or above global median abundance.

data_04b_pathab.txt
----
Generated from data_03b_enzabpgf.txt.
Naively calculated pathway abundance measure, i.e. relative "copy number" of each pathway in the sample.  Calculated for this example as average abundance of all enzymes in the pathway.
