HUMAnN: The HMP Unified Metabolic Analysis Network
====
Curtis Huttenhower, chuttenh@hsph.harvard.edu

HUMAnN is a pipeline for efficiently and accurately determining the presence/absence and abundance of microbial pathways in a community from metagenomic data.  Sequencing a metagenome typically produces millions of short DNA/RNA reads.  HUMAnN takes these reads as inputs and produces gene and pathway summaries as outputs:

* The abundance of each orthologous gene family in the community.  Orthologous families are groups of genes that perform roughly the same biological roles.  HUMAnN uses the KEGG Orthology (KO) by default, but any catalog of orthologs can be employed with minor changes (COG, NOG, etc.)

* The presence/absence of each pathway in the community.  HUMAnN refers to pathway presence/absence as "coverage," and defines a pathway as a set of two or more genes.  HUMAnN uses KEGG pathways and modules by default, but again can easily be modified to use GO terms or other gene sets.

* The abundance of each pathway in the community, i.e. how many "copies" of that pathway are present.

HUMAnN can thus be used in tandem with any translated BLAST program to convert sequence reads into coverage and abundance tables summarizing the gene families and pathways in a microbial community.  This lets you analyze a collection of metagenomes as a matrix of gene/pathway abundances, just like you might analyze a collection of microarrays.

If you use this software, please cite our paper:
"Metabolic reconstruction for metagenomic data and its application to the human microbiome"
Sahar Abubucker, Nicola Segata, Johannes Goll, Alyxandria M. Schubert, Jacques Izard, Brandi L. Cantarel, Beltran Rodriguez-Mueller, Jeremy Zucker, Mathangi Thiagarajan, Bernard Henrissat, Owen White, Scott T. Kelley, Barbara Methé, Patrick D. Schloss, Dirk Gevers, Makedonka Mitreva, Curtis Huttenhower

Many thanks to the NIH and to the entire Human Microbiome Project team for making the HMP possible and for the many collaborators who helped to make HUMAnN a reality.  Sahar Abubucker and Makedonka Mitreva (Washington University) co-led the Metabolic Reconstruction group, the pipeline incorporates software from Yuzhen Ye (Indiana University), Beltran Rodriguez-Mueller (SDSU), and Pat Schloss (University of Michigan), and specific contributors include Alyx Schubert (University of Michigan), Jeremy Zucker (Broad Institute), Brandi Cantarel (UMD), Qiandong Zeng (Broad Institute), Johannes Goll (JCVI), and many others.

BASIC OPERATION
====

HUMAnN uses the scons build system to drive its scientific workflow (see PREREQUISITES).  scons works very much like make, converting a set of inputs into a set of outputs one step at a time, and running only the steps necessary to produce the desired output.  Thus, to analyze your own data:

* Place one or more translated BLAST results using KEGG gene identifiers in the "input" directory (optionally gzipped or bzipped).

* Edit the "SConstruct" file; in particular, make sure that the input processors include one configured for your BLAST file name(s) and format(s).

* Run the "scons" command, optionally parallelizing multiple analyses using the "-j" flag.  Results will be placed in the "output" directory.

HUMAnN is highly configurable in order to perform a collection of very computationally intensive tasks efficiently and flexibly.  Please see the included sample input files, metadata files, and SConstruct settings for an overview of the software's configuration and the file formats it consumes and produces.

PREREQUISITES
====

HUMAnN has no installation per se, but it does depend on the following items:

* A network connection
HUMAnN downloads a number of data and software components from standard repositories during exection.  Please ensure that a network connection is available at the least for the first run.  HUMAnN will use "curl" by default to download files, and this can be changed (e.g. to use "wget") by editing the humann.py file.

* A bunch of RAM
Processing one Illumina lane of metagenomic reads can take as much as ~8-10GB of memory, although it will often take much less depending on the data.  Consider yourself warned.

* scons
http://www.scons.org

* Python >= 2.7
http://www.python.org
As of this writing, we use exactly one feature unique to Python 2.7, math.gamma.  If you're willing to edit it out, the dependency is to Python 2.6 for various modules and syntax.

* blastx
http://www.ncbi.nlm.nih.gov/blast/

Please note that HUMAnN does not run blastx for you.  It instead consumes tabular BLAST results as input.  We recommend the default "-outfmt 6" setting as described below and in the provided SConstruct configuration.  Alternatively, input processors are also provided for accelerated BLAST implementations such as mapx, mblastx, or usearch.

* MinPath (automatically downloaded)
http://omics.informatics.indiana.edu/MinPath/
See Ye et al, PLoS Computational Biology 2009

* BioCyc (optional, automatically downloaded)
http://biocyc.org

* maq (optional, automatically downloaded)
http://maq.sourceforge.net

* R (optional, for synthetic performance evaluation)
http://www.r-project.org

* R package ROCR (optional, for synthetic performance evaluation)
http://rocr.bioinf.mpi-sb.mpg.de

INPUTS
====

One or more tabular translated BLAST (blastx) output files matching sequence read IDs to gene IDs.  Place (or symlink) each file with a .txt, .txt.gz, or .txt.bz extension in the "input" directory before running HUMAnN.  The pipeline includes processors for three tab-delimited text formats by default (below) and can easily by modified to accept more.

As an example, the default inputs provided with HUMAnN were generated using:
  blastx -outfmt 6 -db 28_kegg_genomes < mock_even_lc.fasta.gz | gzip -c > mock_even_lc.txt.gz
Where "28_kegg_genomes" is a database of the amino acid sequences of 28 well-characterized KEGG organisms' ORFs (.pep files from ban, bbr, bqu, bsu, cbo, cdf, cje, eco, efa, ftu, hin, hpy, hsl, lmo, mbo, mtu, ngo, nme, pae, rso, sau, sco, sgo, spn, vch, xfa, yen, and yps).

Please modify the SConstruct file as needed to specify the exact format of your input data:

blastx -outfmt 6
----
qseqid sseqid pident length mismatch gapopen qstart qend sstart send evalue bitscore

mapx
----
template-name frame read-name template-start template-end template-length read-start read-end read-length template-protein read-protein alignment identical %identical positive %positive mismatches raw-score bit-score e-score

mblastx
----
Query_Id Reference_Id E_Value_Bit_Score Identity_Percentage_Length_of_HSP Number_of_Positives_Frame_#s Alignment_Start_in_Query Alignment_End_in_Query Alignment_Start_in_Reference Alignment_End_in_Reference

usearch
----
Note that usearch can be treated identically to "blastx -outfmt 6" if the "--blast6out" flag is provided.

OUTPUTS
====

Three or more files per input including:

* The relative abundances of each gene in the input metagenome.  By default tagged as type "01".  Two columns of tab-delimited text: geneid abundance.

* The coverages of each pathway, expressed as a fraction between 0 and 1 inclusive.  By default tagged as type "04a".  Two columns of tab-delimited text: pathid coverage.

* The relative abundances of each pathway.  By default tagged as type "04b".  Two columns of tab-delimited text: pathid abundance.

* Optionally, a table of individual gene abundances appropriate for loading into METAREP.  By default tagged as type "99".  Five columns of tab-delimited text: geneid abundance e-score %identical identical.  The abundance is relative and calculated as in HUMAnN's gene family abundances; e-score, percent identity, and identity length are averaged over all reads mapping to each gene in the input translated BLAST results.

Three or more merged files are also produced, all tab-delimited text:

* A table containing the relative abundances of all genes in any input metagenomes.  By default named as "01-*.txt".

* A table containing the coverages of all pathways in any input files.  By default named as "04a-*.txt".

* A table containing the relative abundances of all pathways in any input files.  By default named as "04b-*.txt".

* A table containing the relative abundances of all individual genes in any input files.  By default named as "99-*.txt".

Please see below for a detailed description of the ways in which these files are produced and named.

OPTIONAL COMPONENTS
====

You can reproduce the entire performance evaluation using synthetic communities in the HUMAnN manuscript with the tools in the "synth" subdirectory.  This optional step is omitted during default HUMAnN operation but will be automatically incorporated into HUMAnN output if one or more synthetic communities are built.  To do this:

* Place a .fa/.qual file pair or .fastq file in the "synth/output" directory and edit the "synth/SConstruct" file accordingly.  This can be any representative sequencing data from which an error model will be built with which to synthesize artificial reads.

* Unfreeze the synthetic data by changing c_fFrozen to False in SConstruct.  Run "scons" and wait quite a while.  High-quality genomes will be downloaded from KEGG, shredded into artificial reads using maq, and mixed into a synthetic community.

* By default, four communities are built: two with staggered organismal abundances (stg, using a lognormal distribution) and two with even abundances (even), and two with 20 organisms (low complexity, lc) and two with 100 (high complexity, hc).

* The true gene and pathway abundances/coverages will be placed in correspondingly named files in the "synth/output" directory.  These will be automatically detected the next time HUMAnN is executed using scons.  They will be merged into the overall output files, and if correspondingly named input files ("mock_stg_lc*", "mock_even_hc*", etc.) are available, their performance will be automatically plotted as PDF output files using R.

DETAILED OPERATION
====

HUMAnN's scons workflow runs on the assumption that each input file will be converted into one or more output files by combining a series of pipeable processing modules.  It is also set up to allow easy configuration and comparison of output settings, so think of it as a tree: any output processor that _can_ process an input file _will_.  This allows, for example, the quick and easy comparison of the results of metabolic reconstruction using many slightly different parameter settings to determine which is optimal.

Note that while HUMAnN uses primarily KEGG Orthology KO identifiers for genes and KEGG pathway (ko) or module (M) identifiers for pathways, this can be easily modified to suit your analysis needs.  For example, code to process MetaCyc reaction identifiers (for gene families) and pathway identifiers is also included by default.  Any traceable identifiers (ECs, NOGs, etc.) can be used for genes and for the pathways in which they're contained.

The SConstruct file includes a configurable set of processing modules used to convert each input file into one or more outputs.  Processing modules are defined using the CProcessor class with seven arguments:

1. A file suffix (for input files) or type (for output files).  This can be of the form ".txt.gz" for input files or "##" for output files.  This pattern must match the filename _consumed_ by the processor.

2. A file type.  This is of the form "##" by default and can be any short tag (numerical or text) used to identify a type of generated file.  File types are used to chain processing modules together; files of type ## will only and always be further processed by modules that can input type ##.

3. An identifier.  This is of the form "xyz" by default and can be any short tag (numerical or text) used as a human-readable identifier for the processing module and its specific configuration options.  It is appended to the resulting output file and provides a minimal form of data provenance.

4. A program.  This is typically a Python script that consumes an input file on stdin, produces output on stdout, and can optionally include additional command line arguments (see below).

5. Zero or more supporting files as command line arguments.  This array of file names is passed to the processing program as command line arguments (and will be understood by scons as dependencies, thus rebuilding the output when they change).

6. Zero or more additional command line arguments.  This array of arbitrary strings is passed to the processing program as command line arguments (and will be ignored by scons).  This can be used to produce multiple output files from the same processing scripts using command line arguments.

7. A boolean flag, True if the processor should be used for initial input files and False (or omitted) otherwise.  In the latter case, the processor will only be used on intermediate files matching its input type.

8. A boolean flag, True if the output should be gzipped and False (or omitted) otherwise.  Subsequent processors will automatically ungzip compressed input files.

By default, the following output file types are produced:

*_00-*.txt.gz
----
Generated from raw BLAST results.
A condensed binary representation of translated BLAST results, abstracted from and independent of the specific format (blastx/mblastx/mapx) in which they are provided.


*_01-*.txt
----
Generated from *_00-*.txt.gz.
Relative gene abundances as calculated from BLAST results in which each read has been mapped to zero or more gene identifiers based on quality of match.  Total weight of each read is 1.0, distributed over all gene (KO) matches by quality.

*_02a-*.txt
----
Generated from *_01-*.txt.
Relative gene abundances distributed over all pathways in which the gene is predicted to occur.

*_02b-*.txt
----
Generated from *_02a-*.txt.
Relative gene abundances with pathway assignments, taxonomically limited to remove pathways that could only occur in low-abundance/absent organisms.

*_03a-*.txt
----
Generated from *_02b-*.txt.
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

*_99-*.txt
----
Generated from *_00-*.txt.gz.
Per-sample gene abundance tables formatted for loading into METAREP.  On the same relative abundance scale (0 and up) as the original gene abundances _01-*.txt.

04a-*.txt
----
Combined pathway coverage matrix for all samples.

04b-*.txt
----
Combined pathway abundance matrix for all samples, normalized per column.

*_01-keg*.txt
----
Gene abundance calculated as the confidence (e-value/p-value) weighted sum of all hits for each read.

*_02*-mpt*.txt
----
Gene to pathway assignment performed using MinPath.

*_02*-nve*.txt
----
Gene to pathway assignment performed naively using all pathways.

*_02*-cop*.txt
----
Pathway abundances adjusted based on A) taxonomic limitation and B) the expected copy number of each gene in the detected organisms.

*_03a*-wbl*.txt
----
Smoothing performed using Witten-Bell discounting, which shifts sum_observed/(sum_observed + num_observed) probability mass into zero counts and reduces others by the same fraction.

*_03a*-nve*.txt
----
Smoothing performed naively by adding a constant value (0.1) to missing gene/pathway combinations.

*_03b*-nul*.txt
----
No gap filling (no-operation, abundances left as is).

*_03b*-nve*.txt
----
Gap filling by substituting any values below each pathway's median with the median value itself.

*_04a*-nve*.txt
----
Pathway coverage calculated as fraction of genes in pathway at or above global median abundance.

*_04a*-xpe*.txt
----
Pathway coverage calculated as fraction of genes in pathway at or above global median abundance, with low-abundance pathways set to zero using Xipe.

*_04b*-nve*.txt
----
Pathway abundance calculated as average abundance of the most abundant half of genes in the pathway.

NOTES/TROUBLESHOOTING
====

KEGG
----
Since HUMAnN's development, KEGG has gone commercial.  This is a huge blow to the academic community at large, and an unfortunate inconvenience for HUMAnN in particular.  In order to compromise between minimal disruption of HUMAnN operation and respecting KEGG's intellectual property, the following guidelines have been followed:

* Files derived from KEGG necessary for normal HUMAnN operation are included in the data directory.  These include the basic structure of KEGG pathways and modules, gene lengths, and ID/name mappings.

* The more detailed files from KEGG needed for synthetic metagenome construction and evaluation are _not_ included, thus rendering the synth sub-project inoperable without access to KEGG inputs.  We apologize for this inconvenience and urge any impacted users to contact KEGG directly to inform them of the problem.  Please let us know if you're interested in information on additional workarounds to enable synthetic metagenome evaluation.

maq installation issues
----
Some users have reported freezes during the synthetic metagenome maq installation process that are outside of HUMAnN's control.  If maq locks up during compilation or installation, feel free to install it directly from the appropriate Sourceforge package in maq-0.7.1/maq (as expected by HUMAnN) and replace the funcUntarMAQ function in synth/SConstruct with

def funcUntarMAQ( target, source, env ):
    return 0

Note that the synthetic metagenomes are an optional component not needed for normal HUMAnN operation.

Filename restrictions
----
Please do not provide HUMAnN with any input files including _ followed by a digit, e.g. "file_123.txt" or "an_00_example".  HUMAnN uses filename tags of this form to indicate output from each of its processing stages (as described above), and input files that include such patterns should be renamed before HUMAnN execution.

VERSION HISTORY
====

v0.9, 12-06-10
----
* Initial modularization of HUMAnN code
* First application to HMP production data (mblastx)

v0.91, 02-02-11
----
* Refinement of documentation and KEGG/MetaCyc version updates
* Addition of METAREP output module

v0.92, 03-23-11
----
* Addition of full (albeit crummy) CFG parser for KEGG modules
* Improvement to module FPs using X2 for enzyme presence/absence calls

v0.93, 04-26-11
----
* Add default calculation of basic ecology metrics: Shannon, Simpson, Pielou, and richness
* Improve memory usage in METAREP output generation
* Make default Xipe parameters slightly more lenient (retain a few more nonzero pathways)
* Improve gold standard generation in synthetic datasets by retaining full KEGG pathway set

v0.94, 05-03-11
----
* Fix a problem with non-pathway BRITE entities in synthetic gold standard

v0.95, 05-18-11
----
* Fix a typo in hits2enzymes.py (only affected unused filter option)
* Add complete parameter evaluation process to HMP pipeline

v0.96, 07-28-11
----
* MAJOR CHANGE: KEGG is now defunct, and HUMAnN has been updated accordingly
** KEGG derived information needed for normal operation is included
** KEGG files needed for synthetic metagenome construction are _not_ included
** "Frozen" synthetic metagenome evaluation is still possible
** Please contact us directly for more information if needed
* Add documentation on potential maq issues (thanks to Shinichi Sunagawa!)
* Fix a typo in fastq2fasta.py formatting (thanks to Shinichi Sunagawa!)
* Fix a typo in module2modulec.py formatting (thanks to Kathryn Iverson!)
* Fix a typo in eco.py for overly sparse input files (thanks to Jeffrey Werner!)
* Work around Mac OS X zcat issues (thanks to Jeffrey Werner!)

v0.97, 10-17-11
----
* Add several internal evaluation pipelines in response to initial reviews
* Fix hits2*.py handling of zero/very small e-values (thanks to Fah Sathira!)

v0.971, 10-17-11
----
* Fix missing exclude.py (thanks to Brandi Cantarel!)

v0.98, 12-06-11
----
* Allow module2modulec.py to remove unusual duplicate enzymes from KEGG's files
* Allow input filenames to contain underscores
* Fix module size calculation in filter.py
* Fix a bug in hits2enzymes.py to allow a wider range of KEGG gene name detection
