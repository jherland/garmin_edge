#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import math

def haversine(a, b):
    """Calculate great-circle distance between two points on a unity sphere

    The two points are given by their latitudes and longitudes in a.lat/b.lat
    and a.lon/b.lon, respectively. The latitudes/longitudes are assumed to be
    in radians, i.e. latitudes between -π/2 (south) and +π/2 (north), and
    longitudes between -π (west) and +π (east).

    The returned great-circle distance is given in units of sphere radii, i.e.
    multiply the returned value by the actual sphere radius to get the distance
    on an actual sphere.
    """
    d_lat, d_lon = b.lat - a.lat, b.lon - a.lon # differential lat/lon
    c = pow(math.sin(d_lat / 2), 2) + \
        math.cos(a.lat) * math.cos(b.lat) * pow(math.sin(d_lon / 2), 2)
    return 2 * math.asin(math.sqrt(c))

def geodistance(a, b):
    """Calculate the distance in meters between the two given geographic coords

    The geographic coordinates must be given in a.lat/a.lon and b.lat/b.lon in
    units of radians, i.e. latitudes between -π/2 (south) and +π/2 (north), and
    longitudes between -π (west) and +π (east).
    """
    return haversine(a, b) * 6378137.0 # scale by earth radius in m (WGS-84)

class ActSampleDiff(object):
    """Encapsulate the difference between to FitSamples."""

    @classmethod
    def diffs_between_samples(cls, samples):
        prev = next(samples)
        for s in samples:
            yield cls(prev, s)
            prev = s

    def __init__(self, a, b):
        self.t = b.t - a.t # time diff: s
        self.gps_d = geodistance(a, b) # geographic distance from a to b: m
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

def main(path):
    from act_parser import ActParser
    print "Reading activity data from %s..." % (path),
    ap = ActParser(path)
    print "done"
    distances = [0.0, 0.0]
    for n, d in enumerate(ActSampleDiff.diffs_between_samples(ap.samples())):
        distances[0] += d.gps_d
        distances[1] += d.d
        print "%6d: %s" % (n, d)
    print "Total distance: %5.2fm vs. %5.2fm" % (distances[0], distances[1])
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(*sys.argv[1:]))
