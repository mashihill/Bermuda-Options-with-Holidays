#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import division
from math import *
import scipy.stats
import datetime

def tradingDuration(startDate, endDate):

    startDate = [ int(x) for x in startDate.split('-') ]
    endDate = [ int(x) for x in endDate.split('-') ]
    t0 = datetime.date(*startDate)
    t1 = datetime.date(*endDate)
    daygenerator = (t0 + datetime.timedelta(x + 1) for x in xrange((t1 - t0).days))
    duration = sum(1 for day in daygenerator if day.weekday() < 5) 
    duration += 1

    return duration


def BOPF(data):

    totalTradingDays = tradingDuration(data['T0'], data['T1'])
    exercisableDays = tradingDuration(data['T2'], data['T3'])
    yearTradingDays = tradingDuration(data['T0'][0:5]+'01-01', data['T0'][0:5]+'12-31')

    print 'hi', tradingDuration('2015-04-15', '2015-04-16')

    # Initial value
    S = data['S']
    X = data['X']
    m = data['m']
    t = float(totalTradingDays) / yearTradingDays
    n = totalTradingDays * m 
    s = data['s'] / 100  # convert from percentage to decimal
    r = data['r'] / 100
    u = exp(s * sqrt(t / n))
    d = 1 / u   # d = exp(-s * sqrt(t / n))
    r_ = r * t / n
    R = exp(r_)
    a = ceil(log(X / (S * (d ** n))) / log(u / d))  # Smallest int S_T >= X
    p = (R - d) / (u - d)  # Risk-neutral P

    # European Options
    CallSum1 = CallSum2 = 0
    PutSum1 = PutSum2 = 0

    for _ in range(int(a), n):
        CallSum1 += scipy.stats.binom.pmf(_, n, p * u / R)
        CallSum2 += scipy.stats.binom.pmf(_, n, p)

    for _ in range(int(a)):
        PutSum1 += scipy.stats.binom.pmf(_, n, p * u / R)
        PutSum2 += scipy.stats.binom.pmf(_, n, p)

    EuroCall = S * CallSum1 - X * exp(-r_ * n) * CallSum2
    EuroPut = X * exp(-r_ * n) * PutSum2 - S * PutSum1


    # America put
    # Initialize Value at time t
    PutValueFlow = [max(X - (S * (u ** (n-i)) * (d ** i)), 0) for i in range(n+1)]

    print 'exercisableDays', exercisableDays
    # Run backward to time 0
    exercisableDays -= 1
    count = 0
    for time in reversed(range(n)):
        print time
        count += 1
        # Payoff of early exercise
        EarlyExercise = [max(X - (S * (u ** (time-i)) * (d ** i)), 0) for
                         i in range(time+1)]
        # Continuation value
        PutValueFlow = [((p * PutValueFlow[i] + (1-p) * PutValueFlow[i+1]) / R) for
                     i in range(time+1)]

        # Find the larger value
        #if (time in range(n - exercisableDays * m, n) and (time % 2 == 1)):
        #if (count < exercisableDays * m) and (time % 2 == 0):
        if (count <= exercisableDays * m) :
            print 'hi'
            PutValueFlow = [max(EarlyExercise[i], PutValueFlow[i]) for
                         i in range(len(PutValueFlow))]


    # Output Information

    outputs = [ ('Bermuda Call', str(EuroCall)),
               ('Bermuda Put', str(PutValueFlow[0]))]

    # Aligned output
    print "S=%r, X=%r, s=%r%%, t=%r, n=%r, r=%r %%:" % (S, X, data['s'],
                                                        t, n, data['r'])
    for output in outputs:
        print "- {item:13}: {value[0]:>4}.{value[1]:<12}".format(
              item=output[0], value=output[1].split('.') if
              '.' in output[1] else (output[1], '0'))


import sys
import json
if __name__ == '__main__':
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location) as data_file:
            data = json.load(data_file)
        for test in data:
            BOPF(test)
        #print "~~ end ~~"
    else:
        print 'This requires an input file.  Please select one from the data \
               directory. (e.g. python HW3.py ./data)'
