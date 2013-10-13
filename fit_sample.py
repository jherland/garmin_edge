#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import sys
import math
import time
from datetime import datetime

sys.path.append("./python-fitparse")
from fitparse import Activity

class FitSample(object):
    """Encapsulate one sample from a .fit file."""

    @classmethod
    def from_fit_record(cls, r, last_sample):
        d = r.as_dict()
        return cls(
            time.mktime(d['timestamp'].timetuple()),
            d.get('position_lat', last_sample.lat),
            d.get('position_long', last_sample.lon),
            d.get('altitude', last_sample.alt),
            d.get('temperature', last_sample.temp),
            d.get('distance', last_sample.d),
            d.get('speed', last_sample.v),
            d.get('heart_rate', last_sample.hr),
            d.get('cadence', last_sample.cad),
        )

    @classmethod
    def all_from_fit_file(cls, path):
        act = Activity(path)
        act.parse()
        # TODO: Detect timer start event and use that to reset timestamps.
        s = cls(0, 0, 0, 0.0, 0.0, 0.0, 0.0, 0, 0)
        for r in act.get_records_by_type('record'):
            s = cls.from_fit_record(r, s)
            yield s

    def __init__(self, t, lat, lon, alt, temp, d, v, hr, cad):
        self.t = t # seconds since start/epoch: s
        self.lat = lat # latitude: semicircles (= 180/(2**31) degrees)
        self.lon = lon # longitude: semicircles (= 180/(2**31) degrees)
        self.alt = alt # altitude: m
        self.temp = temp # temperature: °C
        self.d = d # distance: m
        self.v = v # speed: m/s
        self.hr = hr # heart rate: bpm
        self.cad = cad # cadence: rpm

    def __str__(self):
        return "<%s at %s, %s, %6.1fm.a.s., %4.1f°C, %6dm, %4.1fm/s, " \
               "%3dbpm, %3drpm>" % (self.__class__.__name__,
                self.pos_str(), self.iso_timestamp(), self.alt, self.temp,
                self.d, self.v, self.hr, self.cad)

    def copy(self):
        return self.__class__(self.t, self.lat, self.lon, self.alt, self.temp,
                              self.d, self.v, self.hr, self.cad)

    def iso_timestamp(self):
        return datetime.fromtimestamp(self.t).replace(microsecond=0).isoformat(" ")

    @staticmethod
    def semicircles_to_deg(semicircles):
        """Convert integer value of semicircles to degrees."""
        return float(semicircles) * 180 / 2**31

    def lat_deg(self):
        """Return latitude as degrees (positive = north, negative = south)."""
        return self.semicircles_to_deg(self.lat)

    def lon_deg(self):
        """Return longitude as degrees (positive = east, negative = west)."""
        return self.semicircles_to_deg(self.lon)

    @staticmethod
    def semicircles_to_rad(semicircles):
        """Convert integer value of semicircles to radians."""
        return float(semicircles) * math.pi / 2**31

    def lat_rad(self):
        """Return latitude as radians (positive = north, negative = south)."""
        return self.semicircles_to_rad(self.lat)

    def lon_rad(self):
        """Return longitude as radians (positive = east, negative = west)."""
        return self.semicircles_to_rad(self.lon)

    def lat_coord(self):
        """Return latitude as (dir, degrees) tuple where dir is 'N' or 'S'."""
        deg = self.lat_deg()
        c = "N" if deg >= 0 else "S"
        return (c, abs(deg))

    def lon_coord(self):
        """Return longitude as (dir, degrees) tuple where dir is 'E' or 'W'."""
        deg = self.lon_deg()
        c = "E" if deg >= 0 else "W"
        return (c, abs(deg))

    def pos_str(self, sep=" "):
        """Return latitude/longitude as string, like "N59.810266, E010.910737".

        Supply 'sep' to customize the separator between the two components.
        """
        lat, lon = self.lat_coord(), self.lon_coord()
        return "%c%09.6f%s%c%010.6f" % (lat[0], lat[1], sep, lon[0], lon[1])

    def apply(self, func, *args):
        """Perform self.X = func("X", self, *args) for each attr X in self."""
        for attr in ['t', 'lat', 'lon', 'alt', 'temp', 'd', 'v', 'hr', 'cad']:
            setattr(self, attr, func(attr, self, *args))

def main(fitpath):
    print "Reading .fit data from %s..." % (fitpath)
    for n, s in enumerate(FitSample.all_from_fit_file(fitpath)):
        print "%6d: %s" % (n, s)
    return 0

if __name__ == '__main__':
    sys.exit(main(*sys.argv[1:]))
