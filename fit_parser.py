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

class FitParser(object):
    @staticmethod
    def from_fit_record(r, last_sample):
        d = r.as_dict()
        try:
            lat = semicircles_to_radians(d['position_lat'])
        except KeyError:
            lat = last_sample.lat
        try:
            lon = semicircles_to_radians(d['position_long'])
        except KeyError:
            lon = last_sample.lon
        return ActSample(
            time.mktime(d['timestamp'].timetuple()),
            lat,
            lon,
            d.get('altitude', last_sample.alt),
            d.get('temperature', last_sample.temp),
            d.get('distance', last_sample.d),
            d.get('speed', last_sample.v),
            d.get('heart_rate', last_sample.hr),
            d.get('cadence', last_sample.cad),
        )

    @classmethod
    def samples(cls, path):
        act = Activity(path)
        act.parse()
        # TODO: Detect timer start event and use that to reset timestamps.
        s = ActSample.empty()
        for r in act.get_records_by_type('record'):
            s = cls.from_fit_record(r, s)
            yield s

def main(fitpath):
    print "Reading .fit data from %s..." % (fitpath)
    for n, s in enumerate(FitParser.samples(fitpath)):
        print "%6d: %s" % (n, s)
    return 0

if __name__ == '__main__':
    sys.exit(main(*sys.argv[1:]))
