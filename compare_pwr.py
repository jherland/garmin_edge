#!/usr/bin/env python2

import sys

from act_sample_norm import normalize
from correlate_activities import correlated_samples, by_key


def average(value_tuples):
    avg = []
    tlen = len(value_tuples[0])
    for i in range(tlen):
        avg.append(float(sum(t[i] for t in value_tuples)) / len(value_tuples))
    return tuple(avg)


def smoother(value_tuples, window_size=1):
    assert window_size >= 1
    window = []
    for t in value_tuples:
        window.append(t)
        if len(window) > window_size:
            window = window[-window_size:]
        assert len(window) <= window_size
        if len(window) == window_size:
            yield average(window)


def extract_pwr(l1, l2, **correlation_args):
    for a, b in correlated_samples(l1, l2, **correlation_args):
        yield a.pwr, b.pwr


def main(path1, path2, smooth=1, skip=0, stop='inf', low=0, high=9999):
    from act_parser import ActParser
    print "# Reading activity data from %s..." % (path1),
    p1 = ActParser(path1)
    l1 = list(normalize(p1.samples(), ignore_gps=True))
    print "done, read %d samples" % (len(l1))
    print "# Reading activity data from %s..." % (path2),
    p2 = ActParser(path2)
    l2 = list(normalize(p2.samples(), ignore_gps=True))
    print "done, read %d samples" % (len(l2))

    smooth = int(smooth)
    assert smooth >= 1
    skip = int(skip)
    assert skip >= 0
    try:
        stop = int(float(stop))
    except OverflowError:
        stop = sys.maxint
    assert stop > skip
    low = int(low)
    high = int(high)
    assert high > low

    # Correlate by HR (assumes both activities picked up the same HR data.)
    by_hr = by_key(lambda x: x.hr)
    sum1 = sum2 = 0
    n = 0
    for i, (pwr1, pwr2) in enumerate(smoother(extract_pwr(l1, l2, score=by_hr), smooth)):
        if i < skip or (pwr1 + pwr2 < 2 * low) or (pwr1 + pwr2 > 2 * high):
            continue
        if i >= stop:
            break
        sum1 += pwr1
        sum2 += pwr2
        n += 1
        try:
            percent = float(pwr2) / pwr1 * 100
        except ZeroDivisionError:
            percent = float("inf")
        print "%6d: %4dW, %4dW => %3.1f%%"  % (i, pwr1, pwr2, percent)
    percent = float(sum2) / sum1 * 100
    print "Average across %d samples: %4.2fW, %4.2fW => %3.3f%%"  % (
        n,
        float(sum1) / n,
        float(sum2) / n,
        percent)


if __name__ == '__main__':
    import sys
    sys.exit(main(*sys.argv[1:]))
