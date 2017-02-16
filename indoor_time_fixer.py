#!/usr/bin/env python3

# Run as follows:
# ./indoor_time_fixer.py $start_time < input.tcx > output.tcx
#
# Rewrites all timestamps to to 1-second increments from $start_time.
# Used to eliminate time skips caused by the Garmin unit suddenly restting
# its internal clock while in the middle of an indoor workout (probably
# related to intermittent GPS lock while indoors, even though GPS should
# be disabled altogether...)

from datetime import datetime, timedelta
import re


class TimeFixer:
    Pattern = re.compile(
        r'(<Id>|<Lap StartTime="|<Time>)'        # pre
        r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})' # timestamp
        r'(\.000Z(?:</Id>|">|</Time>))')         # post

    def __init__(self, start_time):
        self.t = start_time

    def __call__(self, match):
        pre, timestamp, post = match.groups()
        line = pre + self.t.strftime('%Y-%m-%dT%H:%M:%S') + post
        if pre == '<Time>':
            self.t += timedelta(seconds=1)
        return line


def main(in_f, out_f, start_time):
    fixer = TimeFixer(datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%S'))

    for line in in_f:
        out_f.write(fixer.Pattern.sub(fixer, line))


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.stdin, sys.stdout, sys.argv[1]))
