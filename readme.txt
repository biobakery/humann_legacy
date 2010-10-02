NB
----
All of these files currently use KEGG Orthology KO identifiers for genes and KEGG Pathway identifiers for pathways.  This is for demonstration purposes only and not meant to suggest they'll be the only pathways used in production analyses!  Any traceable identifiers (MetaCyc, EC, etc.) can be used for enzymes and for the pathways in which they're contained.

See SConstruct for specific processing pipeline used to generate each file.
- Each output file is tagged with a number to indicate its stage in the processing pipeline, e.g. "01" for the initial BLAST -> gene output, "03b" for smoothed, gap-filled pathway assignments.
- Each output file is tagged with a three-letter code indicating which module was used to build it at each stage of the pipeline, e.g. "mpt" for MinPath, "nul" for a no-operation dummy module.

*_01-*.txt
----
Generated from raw BLAST results.
Relative gene abundances as calculated from BLAST results in which each read has been mapped to zero or more enzyme identifiers based on quality of match.  Total weight of each read is 1.0, distributed over all gene (KO) matches by quality.

*_02-*.txt
----
Generated from *_01-*.txt.
Relative gene abundances distributed over all pathways in which the gene is predicted to occur.

*_03a-*.txt
----
Generated from *_02-*.txt.
Relative gene abundances with pathway assignments, smoothed so that zero means zero and non-zero values are imputed to account for non-observed sequences.

*_03b-*.txt
----
Generated from *_03a-*.txt.
Relative gene abundances with pathway assignments, gap-filled so that gene/pathway combinations with surprisingly low frequency are imputed to contain a more plausible value.

*_04a-*.txt
----
Generated from *_03b-*.txt.
Pathway coverage (presence/absence) measure, i.e. relative confidence of each pathway being present in the sample.  Values are between 0 and 1 inclusive.

*_04b-*.txt
----
Generated from *_03b-*.txt.
Pathway abundance measure, i.e. relative "copy number" of each pathway in the sample.  On the same relative abundance scale (0 and up) as the original gene abundances _01-*.txt.

*_04a-*.txt
----
Combined pathway coverage matrix for all samples.

*_04b-*.txt
----
Combined pathway abundance matrix for all samples, normalized per column.

*_01-keg*.txt
----
Gene abundance calculated as the confidence (e-value/p-value) weighted sum of all hits for each read.

*_02-*-mpt*.txt
----
Gene to pathway assignment performed using MinPath.

*_02-*-nve*.txt
----
Gene to pathway assignment performed naively using all pathways.

*_03a-*-wbl*.txt
----
Smoothing performed using Witten-Bell discounting, which shifts sum_observed/(sum_observed + num_observed) probability mass into zero counts and reduces others by the same fraction.

*_03a-*-nve*.txt
----
Smoothing performed naively by adding a constant value (0.1) to missing gene/pathway combinations.

*_03b-*-nul*.txt
----
No gap filling (no-operation, abundances left as is).

*_03b-*-nve*.txt
----
Gap filling by substituting any values below each pathway's median with the median value itself.

*_04a-*-nve*.txt
----
Pathway coverage calculated as fraction of genes in pathway at or above global median abundance.

*_04b-*-nve*.txt
----
Pathway abundance calculated as average abundance of all genes in the pathway.
