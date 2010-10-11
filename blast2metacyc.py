#!/usr/bin/env python

from optparse import OptionParser

def parse_uniprot_metacyc_map( filename ):
    tabfile = open(filename, 'r')
    uniprot_metacyc_map = {}
    header = tabfile.readline()
    rxns = {}
    for line in  tabfile:
        rxn_enz = line.split('\t')
        rxn, ec = rxn_enz[:2]
        rxns[(rxn, ec)] = {}
        for enz in rxn_enz[2:]:
            rxns[(rxn,ec)][enz] = 0
            rxns[(rxn,ec)]['total'] = 0
            if enz in uniprot_metacyc_map:
                uniprot_metacyc_map[enz].append( (rxn, ec) )
            else:
                uniprot_metacyc_map[enz] = [(rxn, ec)]
                
    return uniprot_metacyc_map, rxns


def parse_uniprot( line ):
    cols = line.split('\t')
    return cols[0].split('|')
    
    
def parse_annotation( annotationfile, uniprot_metacyc, rxns ):
    annot = open(annotationfile, 'r')
    for line in annot:
        for uniprot in parse_uniprot( line ):
            if uniprot in uniprot_metacyc:
                for rxn, ec in uniprot_metacyc[uniprot]:
                    rxns[(rxn,ec)][uniprot] +=1
                    rxns[(rxn,ec)]['total'] +=1
    return rxns


def write_abundances( filename, abundance ):
    out = open(filename, 'w')
    out.write('Rxn\tEC\tTotal abundance\tper enzyme abundances\n')
    
    for rxn, ec in sorted( abundance.keys(), cmp=lambda x,y: -cmp(abundance[x]['total'], abundance[y]['total'])):
        out.write('%s\t%s' % (rxn, ec) )
        for enz in sorted( abundance[(rxn,ec)], cmp=lambda x,y: -cmp(abundance[(rxn, ec)][x], abundance[(rxn, ec)][y])):
            out.write('\t%s:%d' % (enz, abundance[(rxn,ec)][enz]))
        out.write('\n')
    out.close()

def parseOptions():
    parser = OptionParser()
    parser.add_option("-u", "--uniprot", dest="uniprot_metacyc_mapfile", help="location of Uniprot-MetaCyc mappings file", metavar="UNIPROT-METACYC-MAP")
    parser.add_option("-a", "--alignments", dest="alignmentsfile", help="location of alignments", metavar="ALIGNMENTS")
    parser.add_option("-o", "--output", dest="outputfile", help="name of outputfile", metavar="OUTPUT")
    return parser.parse_args()


if __name__ == '__main__':
    options, args = parseOptions()
    uniprot_metacyc_map, rxns = parse_uniprot_metacyc_map( options.uniprot_metacyc_mapfile )
    abundances = parse_annotation( options.alignmentsfile, uniprot_metacyc_map, rxns )
    write_abundances( options.outputfile, abundances )
