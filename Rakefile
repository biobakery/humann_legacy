C_strInputData				= "data_00_blast.txt"
C_strInputKEGGC				= "keggc"
C_strInputKOC				= "koc"
C_strProgBlast2Enzymes		= "./blast2enzymes.py"
C_strProgEnzymes2Pathways	= "./enzymes2pathways.py"
C_strProgSmoothEnzymes		= "./smooth.py"
C_strProgGapFill			= "./gapfill.py"
C_strProgPathCov			= "./pathcov.py"
C_strProgPathAb				= "./pathab.py"
C_strFile01EnzAb			= "data_01_enzab.txt"
C_strFile02EnzAbP			= "data_02_enzabp.txt"
C_strFile03aEnzAbPSm		= "data_03a_enzabpsm.txt"
C_strFile03bEnzAbPGf		= "data_03b_enzabpgf.txt"
C_strFile04aPathCov			= "data_04a_pathcov.txt"
C_strFile04bPathAb			= "data_04b_pathab.txt"

file C_strFile01EnzAb => [C_strInputData, C_strProgBlast2Enzymes,
	C_strInputKOC] do |pT|
	sh pT.prerequisites[1] + " " + C_strInputKOC + " < " +
		pT.prerequisites[0] + " > " + pT.name
end

file C_strFile02EnzAbP => [C_strFile01EnzAb, C_strProgEnzymes2Pathways,
	C_strInputKEGGC] do |pT|
	sh pT.prerequisites[1] + " " + C_strInputKEGGC + " < " +
		pT.prerequisites[0] + " > " + pT.name
end

file C_strFile03aEnzAbPSm => [C_strFile02EnzAbP, C_strProgSmoothEnzymes,
	C_strInputKEGGC] do |pT|
	sh pT.prerequisites[1] + " " + C_strInputKEGGC + " < " +
		pT.prerequisites[0] + " > " + pT.name
end

file C_strFile03bEnzAbPGf => [C_strFile03aEnzAbPSm, C_strProgGapFill,
	C_strInputKEGGC] do |pT|
	sh pT.prerequisites[1] + " " + C_strInputKEGGC + " < " +
		pT.prerequisites[0] + " > " + pT.name
end

file C_strFile04aPathCov => [C_strFile03bEnzAbPGf, C_strProgPathCov,
	C_strInputKEGGC] do |pT|
	sh pT.prerequisites[1] + " " + C_strInputKEGGC + " < " +
		pT.prerequisites[0] + " > " + pT.name
end

file C_strFile04bPathAb => [C_strFile03bEnzAbPGf, C_strProgPathAb,
	C_strInputKEGGC] do |pT|
	sh pT.prerequisites[1] + " " + C_strInputKEGGC + " < " +
		pT.prerequisites[0] + " > " + pT.name
end

task :default => [C_strFile01EnzAb, C_strFile02EnzAbP,
	C_strFile03aEnzAbPSm, C_strFile03bEnzAbPGf,
	C_strFile04aPathCov, C_strFile04bPathAb] do
end
