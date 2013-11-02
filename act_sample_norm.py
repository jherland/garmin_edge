#!/usr/bin/env python2
# -*- coding: utf-8 -*-

latlon_zero_threshold = 0.000001 # radians

def normalize(samples):
    """Normalize sample streams to ease stream comparisons.

    The normalization of a sample stream consist of:
     - Insert missing samples so that there is exactly one sample per second
       in the resulting stream
       TODO: Inserted samples should smoothly transition between existing
             samples.
     - Discard obviously bogus samples
    """
    pre = None
    for post in samples:
        if pre is None: # Discard samples until we have a GPS fix
            if abs(post.lat) + abs(post.lon) < latlon_zero_threshold:
                continue # No GPS fix yet...
            else:
                pre = post
        else:
            # Yield all samples in [pre, post)
            while int(pre.t) < int(post.t):
                yield pre
                pre = pre.replace(t = pre.t + 1)
            pre = post
    yield post

def main(path):
    from act_parser import ActParser
    print "Reading activity data from %s..." % (path),
    ap = ActParser(path)
    print "done"
    for n, s in enumerate(normalize(ap.samples())):
        print "%6d: %s" % (n, s)
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(*sys.argv[1:]))
