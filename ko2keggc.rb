#!/usr/bin/env ruby

strKO = nil
hashKEGGs = {}
STDIN.each do |strLine|
	if( strLine =~ /^ENTRY\s+(K\d+)/ )
		strKO = $1
	elsif( strLine =~ /(?:(?:PATH)|(?:BR)):(ko\d+)/ )
#	elsif( strLine =~ /(?:PATH):(ko\d+)/ )
		if( !( astrKOs = hashKEGGs[$1] ) )
			hashKEGGs[$1] = astrKOs = []; end
		astrKOs.push( strKO ); end; end

puts( hashKEGGs.map do |strKEGG, astrKOs|
	strKEGG + "\t" + astrKOs.join( "\t" ); end.join( "\n" ) )
