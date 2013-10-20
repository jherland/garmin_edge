#!/usr/bin/env python2

import sys

from fit_parser import FitParser
from act_sample_diff import ActSampleDiff

class Logger(object):
    enabled = True

    def __init__(self, f=sys.stdout, enabled=None):
        self.f = f
        if enabled is not None:
           self.enabled = enabled

    def error(self, msg):
        if self.enabled:
            print >>self.f, "ERROR: %s" % (msg)

    def warn(self, msg):
        if self.enabled:
            print >>self.f, "WARNING: %s" % (msg)

    def say(self, msg):
        if self.enabled:
            print >>self.f, "%s" % (msg)

logger = Logger()

def main(fitpath):
    print "Reading .fit data from %s..." % (fitpath),
    fp = FitParser(fitpath)
    print "done"
    seconds, records = 0, 0
    gps_dist, int_dist = 0, 0
    dist_diff = 0
    for d in ActSampleDiff.diffs_between_samples(fp.samples()):
        if d.t > 1:
            logger.warn("Lost %ds after %ds" % (d.t - 1, seconds))
        records += 1
        seconds += d.t
        gps_dist += d.gps_d
        int_dist += d.d
        dd = gps_dist - int_dist
        if abs(dd - dist_diff) > 1:
            print "GPS - Int. distance -> %.1fm after %ds" % (dd, seconds)
            dist_diff = dd
    missing = seconds - records
    print "Found %d records in %ds, %d records (=%.2f%%) missing)" % (
        records, seconds, missing, 100.0 * missing / seconds)
    print "Internal distance: %.3fkm" % (int_dist / 1000.0)
    print "Calc. distance from GPS coords: %.3fkm" % (gps_dist / 1000.0)
    print "Int./GPS distance is %.2f%%" % (100.0 * int_dist / gps_dist)

if __name__ == '__main__':
    sys.exit(main(*sys.argv[1:]))
