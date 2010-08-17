require 'logger'

C_strDirInput				= "blast"
C_strDirOutput				= "output"
C_strFileKO					= "ko"
C_strFileKOC				= "koc"
C_strFileKEGGC				= "keggc"
C_logrFileProvenanceTxt		= Logger.new( "provenance.txt" )
C_strProgKO2KOC				= "./ko2koc.rb"
C_strProgKO2KEGGC			= "./ko2keggc.rb"
C_strProgBlast2Enzymes		= "./blast2enzymes.py"
C_strProgEnzymes2Pathways	= "./enzymes2pathways.py"
C_strProgSmoothEnzymes		= "./smooth.py"
C_strProgGapFill			= "./gapfill.py"
C_strProgPathCov			= "./pathcov.py"
C_strProgPathAb				= "./pathab.py"
C_strSuffix00Input			= ".alignments"
C_strSuffix01EnzAb			= "_01-enzab.txt"
C_strSuffix02EnzAbP			= "_02-enzabp.txt"
C_strSuffix03aEnzAbPSm		= "_03a-enzabpsm.txt"
C_strSuffix03bEnzAbPGf		= "_03b-enzabpgf.txt"
C_strSuffix04aPathCov		= "_04a-pathcov.txt"
C_strSuffix04bPathAb		= "_04b-pathab.txt"

def ex( strCmd )

	C_logrFileProvenanceTxt.info( strCmd )
	sh strCmd
end

def rn( pT )

	ex pT.prerequisites[1] + " " + pT.prerequisites[2..-1].join( " " ) +
		" < " + pT.prerequisites[0] + " > " + pT.name
end

def wf( strFrom, strTo, astrDeps, *aArgs )

	strSource = aArgs[0]
	rule( /#{strTo}$/ => [proc {|str|
		if( strSource )
			str = str.sub( /^.*\//, strSource + "/" ); end
		str.sub( /#{strTo}$/, strFrom )}] + astrDeps ) do |pT|
		rn pT
	end
end

file C_strFileKO => [] do |pT|
	ex "wget ftp://ftp.genome.jp/pub/kegg/genes/ko"
end

file C_strFileKOC => [C_strFileKO, C_strProgKO2KOC] do |pT|
	rn pT
end

file C_strFileKEGGC => [C_strFileKO, C_strProgKO2KEGGC] do |pT|
	rn pT
end

wf( C_strSuffix00Input, C_strSuffix01EnzAb,
	[C_strProgBlast2Enzymes, C_strFileKOC], C_strDirInput )

wf( C_strSuffix01EnzAb, C_strSuffix02EnzAbP,
	[C_strProgEnzymes2Pathways, C_strFileKEGGC] )

wf( C_strSuffix02EnzAbP, C_strSuffix03aEnzAbPSm,
	[C_strProgSmoothEnzymes, C_strFileKEGGC] )

wf( C_strSuffix03aEnzAbPSm, C_strSuffix03bEnzAbPGf,
	[C_strProgGapFill, C_strFileKEGGC] )

wf( C_strSuffix03bEnzAbPGf, C_strSuffix04aPathCov,
	[C_strProgPathCov, C_strFileKEGGC] )

wf( C_strSuffix03bEnzAbPGf, C_strSuffix04bPathAb,
	[C_strProgPathAb, C_strFileKEGGC] )

multitask :default do
end
FileList[C_strDirInput + "/*" + C_strSuffix00Input].map do |str|
	strBase = str.sub( /^#{C_strDirInput}/, C_strDirOutput ).sub(
		/#{C_strSuffix00Input}$/, "" )
	multitask :default => strBase + C_strSuffix04aPathCov
	multitask :default => strBase + C_strSuffix04bPathAb
end
