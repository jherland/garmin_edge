#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from act_sample import ActSample

def write_datafile(path, parser, pause_threshold=1):
    f = open(path, "w")
    print >>f, "# Samples from %s:" % (parser.path)
    print >>f, "# time,lat,lon,alt,temp,d,v,hr,cad,pwr"
    prev_t = 0
    for s in parser.samples(ActSample("", "", "", "", "", "", "", "", "", "")):
        if int(s.t) > int(prev_t + pause_threshold):
            print >>f # Insert blank line to signal missing sample(s)
        print >>f, "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s" % (
            s.t, s.lat, s.lon, s.alt, s.temp, s.d, s.v, s.hr, s.cad, s.pwr)
        prev_t = s.t
    f.close()

def main(in_path, out_path, pause_threshold=1):
    from act_parser import ActParser
    print "Reading activity data from %s..." % (in_path),
    ap = ActParser(in_path)
    print "done"

    print "Writing gnuplot data to %s..." % (out_path),
    write_datafile(out_path, ap, int(pause_threshold))
    print "done"

    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(*sys.argv[1:]))
