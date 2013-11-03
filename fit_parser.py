#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import sys
import math
import time

from act_sample import ActSample

sys.path.append("./python-fitparse")
from fitparse import Activity

def semicircles_to_radians(semicircles):
    """Convert integer value of semicircles to radians."""
    return float(semicircles) * math.pi / 2**31

def local_timezone_offset(secs):
    """Return the timezone offset of the local timezone at the given time.

    The returned value is the number of seconds to be added to UTC time to get
    the corresponding local time at the given point in time.
    """
    local, utc = list(time.localtime(secs)), list(time.gmtime(secs))
    local[8], utc[8] = 0, 0
    return time.mktime(local) - time.mktime(utc)

class FitParser(object):
    def __init__(self, path, tz_offset=None):
        self.path = path
        self.tz_offset = tz_offset
        self.act = Activity(path)
        self.act.parse()

    def parseFitRecord(self, r, last_sample):
        d = r.as_dict()
        try:
            lat = semicircles_to_radians(d['position_lat'])
        except KeyError:
            lat = last_sample.lat
        try:
            lon = semicircles_to_radians(d['position_long'])
        except KeyError:
            lon = last_sample.lon
        ts = time.mktime(d['timestamp'].timetuple())
        if self.tz_offset is None:
            self.tz_offset = local_timezone_offset(ts)
        ts -= self.tz_offset
        return ActSample(ts, lat, lon,
            d.get('altitude', last_sample.alt),
            d.get('temperature', last_sample.temp),
            d.get('distance', last_sample.d),
            d.get('speed', last_sample.v),
            d.get('heart_rate', last_sample.hr),
            d.get('cadence', last_sample.cad),
        )

    def samples(self, s=ActSample.empty()):
        """Yield all trackpoints as ActSample objects."""
        for r in self.act.get_records_by_type('record'):
            s = self.parseFitRecord(r, s)
            yield s

    def all(self):
        """Yield all .fit records as dicts."""
        for d in self.act.get_records_as_dicts():
            yield d

def main(fitpath):
    print "Reading .fit data from %s..." % (fitpath),
    fp = FitParser(fitpath)
    print "done"
    for n, s in enumerate(fp.samples()):
        print "%6d: %s" % (n, s)
    return 0

if __name__ == '__main__':
    sys.exit(main(*sys.argv[1:]))
