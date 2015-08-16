#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from fit_parser import FitParser
from tcx_parser import TcxParser
from gpx_parser import GpxParser

class ActParser(object):
    """Frontend for parsers generating ActSamples."""
    def __init__(self, path):
        if path.endswith(".fit"):
            self.p = FitParser(path)
        elif path.endswith(".tcx"):
            self.p = TcxParser(path)
        elif path.endswith(".gpx"):
            self.p = GpxParser(path)
        else:
            raise ValueError("Don't know which parser to use for '%s'" % (path))

    def __getattr__(self, name):
        return getattr(self.p, name)

def main(path):
    print "Reading activity data from %s..." % (path),
    ap = ActParser(path)
    print "done"
    for n, s in enumerate(ap.samples()):
        print "%6d: %s" % (n, s)
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(*sys.argv[1:]))
