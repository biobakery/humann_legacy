#!/usr/bin/env ruby

fDefinition = astrECs = nil
hashMap = {}
STDIN.each do |strLine|
	if( strLine =~ /^ENTRY\s+(\S+)/ )
		hashMap[$1] = astrECs = []
	elsif( strLine =~ /^DEFINITION/ )
		fDefinition = true; end
	if( fDefinition )
		if( strLine !~ /^(?:(?:DEF)|\s)/ )
			fDefinition = false
		else
			while( strLine =~ /(\d+\.\d+\.\d+\.\d+)(.*)/ )
				astrECs.push( $1 )
				strLine = $2; end; end; end; end
hashMap.each do |strKO, astrECs|
	if( astrECs.length > 0 )
		puts( ( [strKO] + astrECs ).join( "\t" ) ); end; end
