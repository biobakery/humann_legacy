READ ME FIRST!!!
----

This directory contains a mini-project for automatically constructing one or more synthetic microbial communities using reference genomes and annotations from KEGG.  By default, four communities are constructed (owing much inspiration to Mavromatis et al 2007):

* A low-complexity community consisting of the 20 organisms specified in organisms_lc.txt.
* A high-complexity community consisting of 100 automatically, randomly selected organisms.
* An even version of each community in which all organisms are equally abundant.
* A staggered version of each community in which different provided (lc) or lognormally distributed (hc) abundances are used.

***PLEASE NOTE*** that this is not as "pretty" a pipeline as HUMAnN (such as it is), and there are some order dependencies; please follow these steps carefully:

1. Like the rest of HUMAnN, this project was originally created assuming public availability of KEGG; this is no longer the case.  A "frozen" evaluation can still be executed as long as an Internet connection is available (to download MAQ etc.), but KEGG genome information can no longer be automatically downloaded.  This will cause builds to fail unless appropriate input files from KEGG are provided manually.  Please contact us if this is an insurmountable issue.

2. In order to build simulated sequencing reads from reference genomes, the pipeline uses a MAQ read error model.  By default, the pipeline will look for a .fa/.qual file pair named "s_1_1_export.fa" and "s_1_1_export.fa.qual" in the input directory from which to build this model.  For obvious reasons, only small demo files are provided with the HUMAnN distribution; please replace these with an appropriate .fa/.qual pair (or .fastq) if you'd like to build a more realistic error model.

3. There is an order dependency in the script: the first time you run scons, output_hc.txt will be built by scanning the KEGG genomes list and randomly selecting manually curated, annotated microbial organisms.  The second time you run scons, 

4. Thus, the quick start guide is: run "scons".  Then run "scons" again.  You'll obtain four primary output files:

* mock_even_lc.fasta, mock_even_hc.fasta, mock_stg_lc.fasta, and mock_stg_hc.fasta containing the simulated reads for four communities.

Plus 12 additional files comprising the gold standard of genes, modules, and pathways in each community:

* mock_((even)|(stg))_[hl]c_01.txt, containing the list of KOs known to be in each community.

* mock_((even)|(stg))_[hl]c_04a.txt, containing the pathway and module coverages of each community.

* mock_((even)|(stg))_[hl]c_04b.txt, containing the pathway and module abundances of each community.
