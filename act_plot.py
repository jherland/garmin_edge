#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from act_sample import ActSample


def average(samples):
    '''Return an average of the given samples.'''
    n = len(samples)
    t = float(sum(s.t for s in samples)) / n
    lat = float(sum(s.lat for s in samples)) / n
    lon = float(sum(s.lon for s in samples)) / n
    alt = float(sum(s.alt for s in samples)) / n
    temp = float(sum(s.temp for s in samples)) / n
    d = float(sum(s.d for s in samples)) / n
    v = float(sum(s.v for s in samples)) / n
    hr = float(sum(s.hr for s in samples)) / n
    cad = float(sum(s.cad for s in samples)) / n
    pwr = float(sum(s.pwr for s in samples)) / n
    return ActSample(t, lat, lon, alt, temp, d, v, hr, cad, pwr)


def smoother(samples, window_size=1):
    '''Generate a stream of samples smoothed by the given window size.'''
    if window_size == 1:
        for s in samples:
            yield s
        return

    assert window_size > 1
    window = []
    for s in samples:
        window.append(s)
        if len(window) > window_size:
            window = window[-window_size:]
        assert len(window) <= window_size
        if len(window) == window_size:
            yield average(window)


def write_datafile(path, parser, pause_threshold=1, offset=0, smooth=1):
    f = open(path, "w")
    print >>f, "# Samples from %s:" % (parser.path)
    print >>f, "# time,lat,lon,alt,temp,d,v,hr,cad,pwr"
    prev_t = 0
    for s in smoother(parser.samples(), smooth):
        if int(s.t) > int(prev_t + pause_threshold):
            print >>f # Insert blank line to signal missing sample(s)
        print >>f, "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s" % (
            s.t + offset, s.lat, s.lon, s.alt, s.temp, s.d, s.v, s.hr, s.cad, s.pwr)
        prev_t = s.t
    f.close()


def main(in_path, out_path, pause_threshold=1, offset=0, smooth=1):
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
