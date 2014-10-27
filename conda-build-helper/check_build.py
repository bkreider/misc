#!/usr/bin/env python
"""
Check to see if the build number conflicts with a local built package.  If
so, set the ENVIRON variable BINSTAR_BUILD_NUMBER with a non-conflicting number
"""

import os
import sys
import os.path
import subprocess
from glob import glob


from conda_build.metadata import MetaData


def load_metadata(path="."):
    return MetaData(path)

def build_cache_dir(meta):
    info = meta.info_index()
    if info["arch"] == "x86_64":
        arch = "64" 
    else:
        arch = "32"

    platform = "{}-{}".format(info["platform"], arch)
    cache_dir = os.path.join(sys.exec_prefix, "conda-bld", platform)
    return cache_dir

def found(name, version, build_number, build_cache):
    filename = os.path.join(build_cache, "{}-{}-{}.tar.bz2".format(name, 
                                                    version, build_number))
    match = glob(filename)
    #print "Filename {} match({})".format(filename, match)
              
    return match

def lookup_build(meta):
    name = meta.name()
    version = meta.version()
    build_number = meta.build_number() 
    build_cache = build_cache_dir(meta)
    
    # Version string has extra pieces: py27_*, py3_*
    splits = meta.build_id().rsplit("_", 1)
    if len(splits) == 2:
        build_extra = "{}_".format(splits[0])
    else:
        build_extra = ""

    for number in xrange(int(build_number),40):
        # look for build version - build string might have py27_<number>
        if not found(name, version, "{}{}".format(build_extra, 
                     number), build_cache):
            if str(number) != build_number:
                print "Changing version number to {}".format(number)
            return str(number)
    
    return None
    
def main():
    path = sys.argv[1]
    meta = load_metadata(path)
    
    number = str(lookup_build(meta))
    if not number:
        print "Couldn't find valid build number to use"
        sys.exit(1)

    os.environ["BINSTAR_BUILD"] = number
    #
    # NEED TO RENAME conda-build so we can monkeypatch
    subprocess.call([".conda-build {}".format(path)], 
        #stdout=sys.stdout,
        #stderr=sys.stderr,
        shell=True)

if __name__ == "__main__":
    main()

