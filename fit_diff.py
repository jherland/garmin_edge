#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import math

class FitDiff(object):
    """Encapsulate the difference between to FitSamples."""

    @classmethod
    def diffs_between_samples(cls, samples):
        prev = next(samples)
        for s in samples:
            yield cls(prev, s)
            prev = s

    @staticmethod
    def coord_dist(a_lat, a_lon, b_lat, b_lon):
        """Calculate the distance in meters between the given two GPS coords.

        The given coords are assumed to be signed 32-bit integers covering the
        range from -180 degrees to +180 degrees. I.e. the given numbers can be
        converted to radians simply by dividing by 2**31.
        """
        d_lat = float(b_lat - a_lat) / 2**31
        d_lon = float(b_lon - a_lon) / 2**31
        a = pow(math.sin(d_lat / 2), 2) + \
            math.cos(float(a_lat) / 2**31) * \
            math.cos(float(b_lat) / 2**31) * \
            pow(math.sin(d_lon / 2), 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return c * 6378137

    def __init__(self, a, b):
        self.t = b.t - a.t # time diff: s
        # distance from a.lat/lon to b.lat/lon: m
        self.latlon_d = self.coord_dist(a.lat, a.lon, b.lat, b.lon)
        self.alt = b.alt - a.alt # altitude diff: m
        self.temp = b.temp - a.temp # temperature diff: °C
        self.d = b.d - a.d # distance from a to b: m
        self.v = b.v - a.v # speed diff: m/s
        self.hr = b.hr - a.hr # heart rate diff: bpm
        self.cad = b.cad - a.cad # cadence diff: rpm

    def __str__(self):
        return "<%s: %+4.1fs, %5.2fm vs. %5.2fm, %+4.1fm/s, %+4.1fm, %+4.1f°C,"\
               " %+3dbpm, %+3drpm>" % (self.__class__.__name__,
                self.t, self.latlon_d, self.d, self.v, self.alt, self.temp,
                self.hr, self.cad)

def main(fitpath):
    from fit_sample import FitSample
    print "Reading .fit data from %s..." % (fitpath)
    diffs = FitDiff.diffs_between_samples(FitSample.all_from_fit_file(fitpath))
    for n, d in enumerate(diffs):
        print "%6d: %s" % (n, d)
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(*sys.argv[1:]))
