#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import sys

from act_parser import ActParser
from act_sample import ActSample
from act_sample_diff import geodistance
from act_sample_norm import normalize

def index_pairs(offset, len1, len2):
    """Generate pair of indices to be scored from the given offset."""
    i = max(-offset, 0)
    j = max(0, offset)
    while i < len1 and j < len2:
        yield (i, j)
        i, j = i + 1, j + 1

def accumulate_score_at_offset(o, l1, l2, score, accumulate, log):
    ret = accumulate(
        [score(l1[i], l2[j]) for i, j in index_pairs(o, len(l1), len(l2))])
    print >>log, o, ret
    return ret

def find_global_max_correlation_offset(l1, l2, score, accumulate, log):
    """Find the offset between l1 and l2 that maximize their correlation.

    We need to find the appropriate offset between l1 and l2 that will line up
    their samples as close as possible to eachother.
    One approach: Imagine we have an offset from -(len(l1) - 1):
        l1: [.........x]
        l2:          [y..............]
    through 0:
        l1: [xxxxxxxxxx]
        l2: [yyyyyyyyyy.....]
    to +(len(l2) - 1):
        l1:               [x.........]
        l2: [..............y]
    where 'x' and 'y' denotes the samples we are pairing, and '.' are the
    samples that fall "outside" the comparison window.

    For a given offset, there is a series of corresponding x/y pairs. For each
    pair, we can call score(x, y) to calculate a score for that pair. We can
    then accumulate the scores for each x/y pair in the comparison window - by
    calling accumulate(scores) - to calculate a total score for that comparison
    window/offset.

    We can now repeat the process for all other offsets/comparison windows,
    and compare the scores to see which offset gives the maximum score. That
    offset will represent the "best" correlation between l1 and l2. We call
    this the (global) maximum correlation offset.

    A straightforward implementation of this algorithm will iterate through all
    windows (from -(len(l1) - 1) to +(len(l2) - 1)) and then accumulate scores
    for each window. Assuming that each score is calculated in constant time
    (O(1)), and each accumulation across a window take time proportional to the
    size of the window (O(len(window))), a full traversal of all windows will
    take O(len(l1) * len(l2)) time. Assuming that the two lists are of roughly
    equal length (= n) (which is typically true for the activities we're trying
    to correlate), we need O(n²) time to find the best correlation.
    """
    maximum = None
    offsets = xrange(-(len(l1) - 1), len(l2))
    for o in offsets:
        s = accumulate_score_at_offset(o, l1, l2, score, accumulate, log)
        if maximum is None or s > maximum[1]:
            maximum = (o, s)
    return maximum

def find_local_max_correlation_offset(l1, l2, score, accumulate, log, start=0):
    """Find the closest offset which corresponds to a local correlation maximum.

    Start looking in either direction from the 'start' offset, and find the
    first offset that corresponds to a local correlation maximum between l1 and
    l2.

    This is a potentially quicker version of the above algorithm, but it
    depends supplying a 'start' offset which is close to the global maximum
    correlation offset. However, here are some good ways to estimate a good
    'start' offset: If the two activity streams to be correlated took place at
    the same time, and the clocks of the two recoding devices were somewhat
    synchronized (e.g. because both devices derived their timestamps from GPS
    clocks), then the offset of corresponding timestamps (i.e. the offset o at
    which l1[x + o].t == l2[x].t for x in [0, min(len(l1), len(l2))) will
    probably be very close to the global correlation maximum. Alternatively, if
    the clocks are not synchronized, but the two devices started recording the
    activity streams roughly simultaneously, then a 'start' offset of 0 will
    probably be close to the global correlation maximum.
    """
    def calc_score(o):
        return accumulate_score_at_offset(o, l1, l2, score, accumulate, log)

    min_offset = -(len(l1) - 1)
    max_offset = len(l1) - 1
    assert min_offset <= start <= max_offset

    s = calc_score(start)
    if start > min_offset:
        r = calc_score(start - 1)
    else:
        r = s
    if start < max_offset:
        t = calc_score(start + 1)
    else:
        t = s

    # Find which direction to search (+1 or -1)
    if s >= max(r, t):
        return (start, s) # Right on
    elif r > t:
        d = -1
    elif t > r:
        d = +1
    else:
        raise NotImplementedError("TODO: Extend r and t until they differ")
    assert d == -1 or d == +1

    max_o, max_s, o = start, s, start + d
    while min_offset <= o <= max_offset:
        s = calc_score(o)
        if s < max_s:
            break # Found local maximum at max_o/max_s
        max_o, max_s, o = o, s, o + d

    return (max_o, max_s)

def closer(a, b):
    """Return a score that's higher, the closer a and b are to eachother."""
    return -geodistance(a, b)

def avg(seq):
    return float(sum(seq)) / len(seq)

def main(path1, path2, logfile=None):
    if logfile:
        log = open(logfile, "w")
    else:
        log = sys.stdout

    print >>log, "# Reading activity data from %s..." % (path1),
    p1 = ActParser(path1)
    l1 = list(normalize(p1.samples()))
    print >>log, "done, read %d samples" % (len(l1))
    print >>log, "# Reading activity data from %s..." % (path2),
    p2 = ActParser(path2)
    l2 = list(normalize(p2.samples()))
    print >>log, "done, read %d samples" % (len(l2))

    o = int(l1[0].t - l2[0].t)
    print >>log, "# Timestamps are offset by %ds" % (o)
    o, score = find_local_max_correlation_offset(l1, l2, closer, avg, log, o)
    print >>log, "# Done: Minimum score at offset %d is %.2f m" % (o, score)
    return 0

if __name__ == '__main__':
    sys.exit(main(*sys.argv[1:]))
