#!/usr/bin/env python2

from act_sample_norm import normalize
from correlate_activities import correlated_samples, by_key

def main(path1, path2):
    from act_parser import ActParser
    print "# Reading activity data from %s..." % (path1),
    p1 = ActParser(path1)
    l1 = list(normalize(p1.samples(), ignore_gps=True))
    print "done, read %d samples" % (len(l1))
    print "# Reading activity data from %s..." % (path2),
    p2 = ActParser(path2)
    l2 = list(normalize(p2.samples(), ignore_gps=True))
    print "done, read %d samples" % (len(l2))

    by_hr = by_key(lambda x: x.hr)
    for i, (a, b) in enumerate(correlated_samples(l1, l2, score=by_hr)):
        print "%6d: %s"  % (i, a)
        print "        %s" % (b)

if __name__ == '__main__':
    import sys
    sys.exit(main(*sys.argv[1:]))
