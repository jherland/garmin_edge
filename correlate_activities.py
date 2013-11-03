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

    print >>log, "# Timestamps are offset by %ss" % (l1[0].t - l2[0].t)
    offs, score = find_global_max_correlation_offset(l1, l2, closer, avg, log)
    print >>log, "# Done: Minimum score is %f.2 m at offset %d" % (score, offs)
    return 0

if __name__ == '__main__':
    sys.exit(main(*sys.argv[1:]))
