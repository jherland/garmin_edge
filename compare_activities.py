#!/usr/bin/env python2

from act_parser import ActParser
from act_sample import ActSample

def main(path1, path2):
    print "Reading activity data from %s..." % (path1),
    p1 = ActParser(path1)
    print "done"
    print "Reading activity data from %s..." % (path2),
    p2 = ActParser(path2)
    print "done"

    compfunc = ActSample.comparator(alt=0.25, d=0.1, v=0.1, hr=0.1, cad=0.1)
    for s1, s2 in zip(p1.samples(), p2.samples()):
        if compfunc(s1, s2):
            print "-%s" % (s1)
            print "+%s" % (s2)
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(*sys.argv[1:]))
