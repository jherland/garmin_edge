#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from act_sample import ActSample

latlon_zero_threshold = 0.000001 # radians

def w_avg(a, b, w):
    """Return weighted average of a and b: a * (1 - w) + b * w."""
    return a * (1 - w) + b * w

def weighted_sample(a, b, w):
    """Return an intermediate sample between a and b, weighted by w.

    The weight w (between 0 and 1) determines how the generated sample are
    relatively influenced by a and b: w == 0 means all a, w == 1 means all b,
    and w == 0.5 means halfway between a and b.
    """
    return ActSample(
        t = w_avg(a.t, b.t, w),
        lat = w_avg(a.lat, b.lat, w),
        lon = w_avg(a.lon, b.lon, w),
        alt = w_avg(a.alt, b.alt, w),
        temp = w_avg(a.temp, b.temp, w),
        d = w_avg(a.d, b.d, w),
        v = w_avg(a.v, b.v, w),
        hr = w_avg(a.hr, b.hr, w),
        cad = w_avg(a.cad, b.cad, w),
        pwr = w_avg(a.pwr, b.pwr, w),
    )

def generate_intermediates(a, b):
    """Generate fake intermediate samples in range [a, b).

    Yield a, then yield intermediate samples for each missing second between a
    and b, that smoothly transition from a towards b. Yield them all up to -
    but not including - b.
    """
    dt = int(b.t) - int(a.t)
    for i in range(dt):
        yield weighted_sample(a, b, i / float(dt))

def normalize(samples):
    """Normalize sample streams to ease stream comparisons.

    The normalization of a sample stream consist of:
     - Insert missing samples so that there is exactly one sample per second
       in the resulting stream
     - Discard obviously bogus samples
    """
    a = None
    for b in samples:
        if a is None: # Discard samples until we have a GPS fix
            if abs(b.lat) + abs(b.lon) < latlon_zero_threshold:
                continue # No GPS fix yet...
            else:
                a = b
        else:
            for s in generate_intermediates(a, b):
                yield s
            a = b
    yield b # Last sample

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
