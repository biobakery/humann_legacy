#!/usr/bin/ruby

if( ARGV.length != 1 )
	raise( "Usage: postprocess_names.rb <named.pcl> < <unnamed.pcl>" ); end
strNamed = ARGV[ 0 ]

hashNames = {}
IO.foreach( strNamed ) do |strLine|
	astrLine = strLine.chomp.split( /\t/ )
	if( astrLine[ 1 ].length > 0 )
		hashNames[ astrLine[ 0 ] ] = astrLine[ 1 ]; end; end

STDIN.each do |strLine|
	astrLine = strLine.chomp.split( /\t/ )
	astrLine.insert( 1, "" )
	if( $. == 1 )
		astrLine[ 1 ] = "NAME"
	else
		astrLine[ 1 ] = hashNames[ astrLine[ 0 ] ]; end
	puts( astrLine.join( "\t" ) ); end
