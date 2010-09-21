#!/usr/bin/env ruby

strID = nil
hashMap = {}
STDIN.each do |strLine|
	if( strLine =~ /^ENTRY\s+(\S+)/ )
		strID = $1
	elsif( strLine =~ /^(?:DBLINKS)?\s*COG:(.+)$/ )
		hashMap[strID] = $1.strip.split( /\s+/ ); end; end
puts( hashMap.map do |strKO, astrCOGs|
	( [strKO] + astrCOGs ).join( "\t" ); end )
