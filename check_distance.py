#!/usr/bin/env python2

import sys

from fit_sample import FitSample

def main(fitpath):
    print "Reading .fit data from %s..." % (fitpath)
    samples = FitSample.all_from_fit_file(fitpath)
    first = next(samples)
    mins = first.copy()
    maxes = first.copy()
    sums = first.copy()
    for n, s in enumerate(samples, 1):
        mins.apply(lambda a, mins: min(getattr(mins, a), getattr(s, a)))
        maxes.apply(lambda a, maxes: max(getattr(maxes, a), getattr(s, a)))
        sums.apply(lambda a, sums: getattr(sums, a) + getattr(s, a))
        n += 1
    print "Processed %d records." % (n)
    print "Minimums:", mins
    print "Maximums:", maxes
    sums.apply(lambda a, sums: getattr(sums, a) / float(n))
    print "Averages:", sums
    return 0

if __name__ == '__main__':
    sys.exit(main(*sys.argv[1:]))
