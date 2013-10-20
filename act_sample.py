#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import math
from datetime import datetime

class ActSample(object):
    @classmethod
    def empty(cls):
        return cls(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

    def __init__(self, t, lat, lon, alt, temp, d, v, hr, cad):
        self.t = t # seconds since start/epoch: s
        self.lat = lat # latitude: radians (-π/2 (south) .. +π/2 (north))
        self.lon = lon # longitude: radians (-π (west) .. +π (east))
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

    @staticmethod
    def comparator(**kwds):
        """Return a comparison function based on the given fields.

        Create and return a function that compares two ActSamples on the fields
        that are non-False in the given argument list. For each (enabled) field,
        the comparison yields 0 (= equality) if the difference between the
        two field values is less than the given value for the field argument.
        The default comparison function returned, will return 0 iff all of the
        following hold:
         - a.t and b.t are <= 0.1 seconds apart
         - a.lat and b.lat are <= 0.0000001 radians apart
         - a.lon and b.lon are <= 0.0000001 radians apart
        The default limits on the lat and lon fields correspond roughly to a
        and b being less than 1m apart in geodistance.
        """
        d = {'t': 0.1, 'lat': 0.0000001, 'lon': 0.0000001}
        d.update(kwds)

        def compfunc(a, b):
            for f in ['t', 'lat', 'lon', 'alt', 'temp', 'd', 'v', 'hr', 'cad']:
                v = d.get(f, False)
                if v and abs(getattr(b, f) - getattr(a, f)) > v:
                    return getattr(b, f) - getattr(a, f)
            return 0

        return compfunc

    def replace(self, **d):
        """Return a new ActSample where the given fields have been replaced."""
        return self.__class__(d.get("t", self.t), d.get("lat", self.lat),
            d.get("lon", self.lon), d.get("alt", self.alt),
            d.get("temp", self.temp), d.get("d", self.d), d.get("v", self.v),
            d.get("hr", self.hr), d.get("cad", self.cad))

    def iso_timestamp(self):
        return datetime.fromtimestamp(self.t).isoformat(" ")

    def lat_deg(self):
        """Return latitude as degrees (positive = north, negative = south)."""
        return math.degrees(self.lat)

    def lon_deg(self):
        """Return longitude as degrees (positive = east, negative = west)."""
        return math.degrees(self.lon)

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
