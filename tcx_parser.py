#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import time
import math
import xml.etree.cElementTree as ET

from act_sample import ActSample

class TcxParser(object):
    TagPrefix = "{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}"
    TagExtPrefix = "{http://www.garmin.com/xmlschemas/ActivityExtension/v2}"

    @classmethod
    def parsePosition(cls, elm):
        lat = elm.findtext(cls.TagPrefix + "LatitudeDegrees")
        lon = elm.findtext(cls.TagPrefix + "LongitudeDegrees")
        return (math.radians(float(lat)), math.radians(float(lon)))

    @classmethod
    def parseTrackpoint(cls, elm, last_sample):
        d = {}

        # timestamp
        ts = elm.findtext(cls.TagPrefix + "Time")
        assert ts.endswith(".000Z") # Assume all timestamps do this...
        d["t"] = time.mktime(time.strptime(ts[:-5], "%Y-%m-%dT%H:%M:%S"))

        # position
        try:
            pos = cls.parsePosition(elm.find(cls.TagPrefix + "Position"))
            d["lat"], d["lon"] = pos
        except (TypeError, AttributeError):
            pass

        # altitude
        try:
            d["alt"] = float(elm.findtext(cls.TagPrefix + "AltitudeMeters"))
        except TypeError:
            pass

        # distance
        try:
            d["d"] = float(elm.findtext(cls.TagPrefix + "DistanceMeters"))
        except TypeError:
            pass

        # heart rate
        try:
            d["hr"] = int(elm.findtext(cls.TagPrefix + "HeartRateBpm/" +
                                       cls.TagPrefix + "Value"))
        except TypeError:
            pass

        # cadence
        try:
            d["cad"] = int(elm.findtext(cls.TagPrefix + "Cadence"))
        except TypeError:
            pass

        # speed
        try:
            d["v"] = float(elm.findtext(cls.TagPrefix + "Extensions/" +
                                        cls.TagExtPrefix + "TPX/" +
                                        cls.TagExtPrefix + "Speed"))
        except TypeError:
            pass

        return last_sample.replace(**d)

    @classmethod
    def samples(cls, path):
        # TODO: Detect timer start event and use that to reset timestamps.
        s = ActSample.empty()
        for event, elm in ET.iterparse(path):
            if elm.tag == cls.TagPrefix + "Trackpoint": # end TrackPoint
                s = cls.parseTrackpoint(elm, s)
                yield s
            elif elm.tag == cls.TagPrefix + "Activity": # end first Activity
                break # Skip any subsequent Activity

def main(tcxpath):
    print "Reading .tcx data from %s..." % (tcxpath)
    for n, s in enumerate(TcxParser.samples(tcxpath)):
        print "%6d: %s" % (n, s)
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(*sys.argv[1:]))
