#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import time
import math
import xml.etree.cElementTree as ET

from act_sample import ActSample

class TcxParser(object):
    TagPrefix = "{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}"
    TagExtPrefix = "{http://www.garmin.com/xmlschemas/ActivityExtension/v2}"

    def __init__(self, path):
        self.path = path

    def parsePosition(self, elm):
        lat = elm.findtext(self.TagPrefix + "LatitudeDegrees")
        lon = elm.findtext(self.TagPrefix + "LongitudeDegrees")
        return (math.radians(float(lat)), math.radians(float(lon)))

    def parseTrackpoint(self, elm, last_sample):
        d = {}

        # timestamp
        ts = elm.findtext(self.TagPrefix + "Time")
        if ts.endswith(".000Z"):
            end = -5
        else:
            assert ts.endswith("Z")
            end = -1
        d["t"] = time.mktime(time.strptime(ts[:end], "%Y-%m-%dT%H:%M:%S"))

        # position
        try:
            pos = self.parsePosition(elm.find(self.TagPrefix + "Position"))
            d["lat"], d["lon"] = pos
        except (TypeError, AttributeError):
            pass

        # altitude
        try:
            d["alt"] = float(elm.findtext(self.TagPrefix + "AltitudeMeters"))
        except TypeError:
            pass

        # distance
        try:
            d["d"] = float(elm.findtext(self.TagPrefix + "DistanceMeters"))
        except TypeError:
            pass

        # heart rate
        try:
            d["hr"] = int(elm.findtext(self.TagPrefix + "HeartRateBpm/" +
                                       self.TagPrefix + "Value"))
        except TypeError:
            pass

        # cadence
        try:
            d["cad"] = int(elm.findtext(self.TagPrefix + "Cadence"))
        except TypeError:
            pass

        # speed
        try:
            d["v"] = float(elm.findtext(self.TagPrefix + "Extensions/" +
                                        self.TagExtPrefix + "TPX/" +
                                        self.TagExtPrefix + "Speed"))
        except TypeError:
            pass

        # power
        try:
            d["pwr"] = float(elm.findtext(self.TagPrefix + "Extensions/" +
                                          self.TagExtPrefix + "TPX/" +
                                          self.TagExtPrefix + "Watts"))
        except TypeError:
            pass

        return last_sample.replace(**d)

    def samples(self, s=ActSample.empty()):
        # TODO: Detect timer start event and use that to reset timestamps.
        for event, elm in ET.iterparse(self.path):
            if elm.tag == self.TagPrefix + "Trackpoint": # end TrackPoint
                s = self.parseTrackpoint(elm, s)
                yield s
            elif elm.tag == self.TagPrefix + "Activity": # end first Activity
                break # Skip any subsequent Activity

def main(tcxpath):
    print "Reading .tcx data from %s..." % (tcxpath),
    tp = TcxParser(tcxpath)
    print "done"
    for n, s in enumerate(tp.samples()):
        print "%6d: %s" % (n, s)
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(*sys.argv[1:]))
