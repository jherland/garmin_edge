#!/usr/bin/env python3

# Run as follows:
# ./tcx_time_fixer.py \
#   1970-01-01T00:00:00#2017-01-02T03:04:05>2017-02-03T04:05:06 \
#   < input.tcx > output.tcx

from datetime import datetime
import re


TimePattern = re.compile(r'\s*<Time>\s*(.*)\s*</Time>\s*\n')


def parse_arg(arg):
    t_from, rest = arg.split('#')
    t_0, t_1 = rest.split('>')
    t_from = datetime.strptime(t_from, '%Y-%m-%dT%H:%M:%S')
    t_0 = datetime.strptime(t_0, '%Y-%m-%dT%H:%M:%S')
    t_1 = datetime.strptime(t_1, '%Y-%m-%dT%H:%M:%S')
    return t_from, t_1 - t_0


class TimeMapper:
    def __init__(self, *maps):
        self.maps = list(maps)  # list of (datetime, timedelta) pairs

    def map(self, t):
        assert t >= self.maps[0][0]
        delta = None
        for m, d in self.maps:
            if t < m:
                break
            delta = d
        assert delta is not None
        return t + delta

    def __call__(self, match):
        t = datetime.strptime(match.group(1), '%Y-%m-%dT%H:%M:%S.000Z')
        t = self.map(t)
        i, j = match.span(1)
        line = match.group(0)
        return line[:i] + t.strftime('%Y-%m-%dT%H:%M:%S.000Z') + line[j:]


def main(in_f, out_f, *args):
    maptime = TimeMapper(*map(parse_arg, args))

    for line in in_f:
        out_f.write(TimePattern.sub(maptime, line))


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.stdin, sys.stdout, *sys.argv[1:]))
