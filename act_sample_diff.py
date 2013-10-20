#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import math

class ActSampleDiff(object):
    """Encapsulate the difference between to FitSamples."""

    @classmethod
    def diffs_between_samples(cls, samples):
        prev = next(samples)
        for s in samples:
            yield cls(prev, s)
            prev = s

    @staticmethod
    def coord_dist(a_lat, a_lon, b_lat, b_lon):
        """Calculate the distance in meters between the given two GPS coords

        The given coords are assumed to be in radians, i.e. between -π and +π.
        """
        d_lat = b_lat - a_lat
        d_lon = b_lon - a_lon
        a = pow(math.sin(d_lat / 2), 2) + \
            math.cos(a_lat) * math.cos(b_lat) * pow(math.sin(d_lon / 2), 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return c * 6378137 # multiply by earth radius (in meters)

    def __init__(self, a, b):
        self.t = b.t - a.t # time diff: s
        self.gps_d = self.coord_dist( # distance from a.lat/lon to b.lat/lon: m
            a.lat_rad(), a.lon_rad(), b.lat_rad(), b.lon_rad())
        self.alt = b.alt - a.alt # altitude diff: m
        self.temp = b.temp - a.temp # temperature diff: °C
        self.d = b.d - a.d # distance from a to b: m
        self.v = b.v - a.v # speed diff: m/s
        self.hr = b.hr - a.hr # heart rate diff: bpm
        self.cad = b.cad - a.cad # cadence diff: rpm

    def __str__(self):
        return "<%s: %+4.1fs, %5.2fm vs. %5.2fm, %+4.1fm/s, %+4.1fm, %+4.1f°C,"\
               " %+3dbpm, %+3drpm>" % (self.__class__.__name__,
                self.t, self.gps_d, self.d, self.v, self.alt, self.temp,
                self.hr, self.cad)

def main(fitpath):
    from act_sample import ActSample
    print "Reading .fit data from %s..." % (fitpath)
    diffs = ActSampleDiff.diffs_between_samples(
        ActSample.all_from_fit_file(fitpath))
    distances = [0.0, 0.0]
    for n, d in enumerate(diffs):
        distances[0] += d.gps_d
        distances[1] += d.d
        print "%6d: %s" % (n, d)
    print "Total distance: %5.2fm vs. %5.2fm" % (distances[0], distances[1])
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(*sys.argv[1:]))
