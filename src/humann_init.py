#!/usr/bin/env python

import os
import sys
import shutil

USAGE = \
"""
Initialize a HUMAnN working environment in the current directory.
Options:
    -h --help    Show this message and quit
    -v --verbose Tell you all about what I'm doing

"""

args = sys.argv[1:]

if '-h' in args or '--help' in args:
    print USAGE
    sys.exit(1)

verbose = bool('-v' in args or '--verbose' in args)

here = os.path.realpath(os.path.abspath(__file__))
mypath = os.path.split(here)[0]
humann_dir = os.path.abspath(os.path.join(mypath,
                                          ".."))
cwd = os.path.realpath(os.path.abspath('.'))

def basedest(file_from_base, file_from_dest):
    file_from_base = os.path.realpath(os.path.join(humann_dir, file_from_base))
    file_from_dest = os.path.realpath(os.path.join(cwd, file_from_dest))
    log("%s -> %s"%(file_from_base, file_from_dest))
    return file_from_base, file_from_dest

def log(msg):
    if verbose:
        print >> sys.stderr, msg

log("Placing links")
for f in  [ 'README.text', 'src', 'synth']:
    os.symlink(*basedest(f, f))

log("Copying files")
for f in  ['data', 'input', 'SConstruct', 'site_scons']:
    base_file, dest_file = basedest(f, f)
    if os.path.isdir(base_file):
        shutil.copytree(base_file, dest_file)
    else:
        shutil.copy(base_file, dest_file)

log("HUMAnN environment initialized.")
                    
