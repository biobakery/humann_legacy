#!/usr/bin/env ruby

astrIDs = []
ahashMaps = []
hashMap = fGenes = strSpecies = nil
STDIN.each do |strLine|
	if( strLine =~ /^ENTRY\s+(\S+)/ )
		astrIDs.push( $1 )
		ahashMaps.push( hashMap = {} )
	elsif( strLine =~ /^GENES(.+)/ )
		strLine = $1
		fGenes = true; end
	if( !fGenes || ( strLine =~ /^\/\/\// ) )
		fGenes = false
		next; end

	strLine.strip!
	if( strLine =~ /^(\S{3}):\s+(.+)/ )
		strSpecies, strLine = $1, $2; end
	strLine.split( /\s+/ ).each do |strToken|
		astrGenes = ( strToken =~ /^(\S+)\((.+)\)$/ ) ? [$1] : [strToken] # ,$2
		astrGenes.each do |strGene|
			hashMap[strSpecies + "#" + strGene.upcase] = true; end; end; end

astrIDs.each_index do |i|
	if( !ahashMaps[i].empty? )
		puts( astrIDs[i] + "\t" + ahashMaps[i].keys.join( "\t" ) ); end; end

=begin
hashhashMap = {}
strID = fGenes = nil
STDIN.each do |strLine|
	if( strLine =~ /^ENTRY\s+(\S+)/ )
		strID = $1
	elsif( strLine =~ /^GENES(.+)/ )
		strLine = $1
		fGenes = true; end
	if( !fGenes || ( strLine =~ /^\/\/\// ) )
		fGenes = false
		next; end

	strLine.strip!
	if( strLine =~ /^\S{3}:\s+(.+)/ )
		strLine = $1; end
	strLine.split( /\s+/ ).each do |strToken|
		astrGenes = ( strToken =~ /^(\S+)\((.+)\)$/ ) ? [$1, $2] : [strToken]
		astrGenes.each do |strGene|
			strGene.upcase!
			if( !( hashMap = hashhashMap[strGene] ) )
				hashhashMap[strGene] = hashMap = {}; end
			hashMap[strID] = true; end; end; end

hashhashMap.each do |strFrom, hashTo|
	puts( strFrom + "\t" + hashTo.keys.join( "\t" ) ); end
=end