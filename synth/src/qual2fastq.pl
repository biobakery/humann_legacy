#!/usr/bin/perl

use warnings;
use strict;
use File::Basename;

my ($inFasta, $inQual) = @ARGV;

my %seqs;

$/ = ">";

open (FASTA, "<$inFasta");
my $junk = (<FASTA>);

while (my $frecord = <FASTA>) {
	chomp $frecord;
	my ($fdef, @seqLines) = split /\n/, $frecord;
	my $seq = join '', @seqLines;
	$seqs{$fdef} = $seq;
}

close FASTA;

open (QUAL, "<$inQual");
$junk = <QUAL>;

while (my $qrecord = <QUAL>) {
	chomp $qrecord;
	my ($qdef, @qualLines) = split /\n/, $qrecord;
	my $qualString = join ' ', @qualLines;
	my @quals = split / /, $qualString;
	print "@","$qdef\n";
	print "$seqs{$qdef}\n";
	print "+\n";
	foreach my $qual (@quals) {
		print chr($qual + 33);
	}
	print "\n";
}

close QUAL;
