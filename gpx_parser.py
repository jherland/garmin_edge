#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import time
import math
import xml.etree.cElementTree as ET

from act_sample import ActSample

class GpxParser(object):
    TagPrefix = "{http://www.topografix.com/GPX/1/1}"
    TagExtPrefix = "{http://www.garmin.com/xmlschemas/TrackPointExtension/v1}"

    def __init__(self, path):
        self.path = path

    def parsePosition(self, elm):
        lat, lon = elm.get("lat"), elm.get("lon")
        return (math.radians(float(lat)), math.radians(float(lon)))

    def parseTrackpoint(self, elm, last_sample):
        d = {}

        # timestamp
        ts = elm.findtext(self.TagPrefix + "time")
        d["t"] = time.mktime(time.strptime(ts, "%Y-%m-%dT%H:%M:%SZ"))

        # position
        try:
            pos = self.parsePosition(elm)
            d["lat"], d["lon"] = pos
        except (TypeError, AttributeError):
            pass

        # altitude
        try:
            d["alt"] = float(elm.findtext(self.TagPrefix + "ele"))
        except TypeError:
            pass

        # heart rate
        try:
            d["hr"] = int(elm.findtext(
                self.TagPrefix + "extensions/" +
                self.TagExtPrefix + "TrackPointExtension/" +
                self.TagExtPrefix + "hr"))
        except AssertionError: #TypeError:
            pass

        # cadence
        try:
            d["cad"] = int(elm.findtext(
                self.TagPrefix + "extensions/" +
                self.TagExtPrefix + "TrackPointExtension/" +
                self.TagExtPrefix + "cad"))
        except TypeError:
            pass

        return last_sample.replace(**d)

    def samples(self, s=ActSample.empty()):
        # TODO: Detect timer start event and use that to reset timestamps.
        for event, elm in ET.iterparse(self.path):
            if elm.tag == self.TagPrefix + "trkpt": # end TrackPoint
                s = self.parseTrackpoint(elm, s)
                yield s
            elif elm.tag == self.TagPrefix + "trk": # end first Activity
                break # Skip any subsequent Activity

def main(gpxpath):
    print "Reading .gpx data from %s..." % (gpxpath),
    tp = GpxParser(gpxpath)
    print "done"
    for n, s in enumerate(tp.samples()):
        print "%6d: %s" % (n, s)
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(*sys.argv[1:]))
