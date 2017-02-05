#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os

from act_parser import ActParser
from act_plot import write_datafile

CommonCommands = "common.gnuplot"

Columns = [
    (1, "ts",   "Timestamp (s)"),
    (2, "lat",  "Latitude (rad)"),
    (3, "lon",  "Longitude (rad)"),
    (4, "alt",  "Altitude (m.a.s)"),
    (5, "temp", "Temperature (°C)"),
    (6, "d",    "Cumulative Distance (m)"),
    (7, "v",    "Speed (m/s)"),
    (8, "hr",   "Heart Rate (bpm)"),
    (9, "cad",  "Cadence (rpm)"),
    (10, "pwr",  "Power (W)"),
]

class DataFile(object):
    def __init__(self, path):
        path_w_modifiers = path.split(':')
        self.path = path_w_modifiers[0]
        # defaults
        self.pause_threshold = 1
        self.offset = 0
        try:
            self.pause_threshold = int(path_w_modifiers[1])
            self.offset = int(path_w_modifiers[2])
        except IndexError:
            pass
        self.basename, self.ext = os.path.splitext(self.path)
        self.gp_path = self.basename + ".gnuplot"
        self.parser = None

    def __str__(self):
        return "%s:%d:%s" % (self.path, self.pause_threshold, self.offset)

    def parse(self):
        if self.parser is None:
            print "# Parsing activity data from %s..." % (self.path),
            self.parser = ActParser(self.path)
            print "done"

    def write_gnuplot_data(self):
        self.parse()
        print "# Writing gnuplot data to %s..." % (self.gp_path),
        write_datafile(self.gp_path, self.parser, self.pause_threshold, self.offset)
        print "done"

def main(*args):
    shorthands = dict((c[1], c) for c in Columns)
    columns, datafiles = [], []
    for arg in args:
        if arg in shorthands:
            columns.append(shorthands[arg])
        else:
            datafiles.append(DataFile(arg))

    if not columns:
        print "Must specify at least one column (%s)" % (
            ", ".join(shorthands.keys()))
        return 1
    if not datafiles:
        print "Must specify at least one activity file (.fit or .tcx)"
        return 2

    print "# Plotting (%s) from activities %s" % (
        ", ".join(c[2] for c in columns),
        ", ".join(map(str, datafiles)))

    # Produce requires .gnuplot data files
    for df in datafiles:
        df.write_gnuplot_data()

    # Generate plot
    sys.stdout.write(open(CommonCommands).read())
    series = []
    i = 0
    for c in columns:
        for df in datafiles:
            i += 1
            series.append('"%s" using 1:%d with linespoints ls %d' % (
                df.gp_path, c[0], i))

    print "plot", ", ".join(series)

    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(*sys.argv[1:]))
