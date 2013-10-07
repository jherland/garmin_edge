#!/usr/bin/env python2

import sys
import datetime
from pprint import pprint

sys.path.append("./python-fitparse")
from fitparse import Activity

Debug = False

def format_vals(vals):
    return "%8.6fs: %7.3fkm %6.3fkm/h %c%8.6f, %c%8.6f" % (
        vals[0], # Time since last sample [seconds]
        vals[1] / 1000.0, # Elapsed distance [km]
        vals[2] * 3.6 ,# Speed [km/h]
        "N" if vals[3] >= 0 else "S",
        (180.0 * vals[3]) / 2 **31, # Latitude [degrees]
        "E" if vals[3] >= 0 else "W",
        (180.0 * vals[3]) / 2 **31, # Longitude [degrees]
    )

def main(fitpath):
    print "Reading .fit data from %s..." % (fitpath)
    act = Activity(fitpath)
    act.parse()
    records = act.get_records_as_dicts()
    print "Processing .fit records..."
    n = 0
    # when, dist, speed, pos_lat, pos_long
    mins = [None, None, None, None, None]
    maxes = [None, None, None, None, None]
    sums = [0, 0, 0, 0, 0]
    last_when = None
    for r in records:
        if "event" in r and r["event"] == "timer" and r["event_type"] == "start":
            last_when = r["timestamp"]
        elif "distance" not in r:
            if Debug:
                print "Skipping non-record: ",
                pprint(r)
            continue
        try:
            when = r["timestamp"]
            assert isinstance(when, datetime.datetime)
            assert isinstance(last_when, datetime.datetime)
            elapsed = when - last_when
            assert isinstance(elapsed, datetime.timedelta)
            last_when = when
            vals = [elapsed.total_seconds(), r['distance'], r["speed"],
                    r["position_lat"], r["position_long"]]
            pos_lat = (float(r["position_lat"]) / 2**31) * 180
            pos_long = (float(r["position_long"]) / 2**31) * 180
        except KeyError:
            if Debug:
                print "Skipping malformed record: ",
                pprint(r)
            continue
        for i, v in enumerate(vals):
            if mins[i] is None:
                mins[i] = v
            else:
                mins[i] = min(mins[i], v)
            if maxes[i] is None:
                maxes[i] = v
            else:
                maxes[i] = max(maxes[i], v)
            sums[i] += v
        n += 1
    print "Processed %d records." % (n)
    print
    print "          elapse, distance, speed, latitude, longitude"
    print "Minimums:", format_vals(mins)
    print "Maximums:", format_vals(maxes)
    avgs = [float(s) / n for s in sums]
    print "Averages:", format_vals(avgs)
    return 0

if __name__ == '__main__':
    sys.exit(main(*sys.argv[1:]))
