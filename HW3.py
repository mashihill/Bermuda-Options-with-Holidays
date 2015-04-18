#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import division
from math import *
import scipy.stats
import datetime

def dayGenerate(startDate, endDate):

    startDate = [ int(x) for x in startDate.split('-') ]
    endDate = [ int(x) for x in endDate.split('-') ]
    t0 = datetime.date(*startDate)
    t1 = datetime.date(*endDate)
    daylist = [t0 + datetime.timedelta(x) for x in xrange((t1 - t0).days + 1)]

    return daylist

def noHolidayDays(startDate, endDate):
    startDate = [ int(x) for x in startDate.split('-') ]
    endDate = [ int(x) for x in endDate.split('-') ]
    t0 = datetime.date(*startDate)
    t1 = datetime.date(*endDate)
    daygenerator = (t0 + datetime.timedelta(x) for x in xrange((t1 - t0).days + 1))
    duration = sum(1 for day in daygenerator if day.weekday() < 5) 

    return duration


def holidayBefore(startDate, endDate):

    daygenerator = (startDate + datetime.timedelta(x) for x in xrange((endDate - startDate).days))

    return sum(1 for day in daygenerator if day.weekday() >= 5) 


def BOPF(data):

    aliveDuration = dayGenerate(data['T0'], data['T1'])
    exercisableDuration = dayGenerate(data['T2'], data['T3'])
    yearDuration = dayGenerate(data['T0'][0:5]+'01-01', data['T0'][0:5]+'12-31')
    aliveTradingDuration = noHolidayDays(data['T0'], data['T1'])
    exercisableTradingDuration = noHolidayDays(data['T2'], data['T3'])
    yearTradingDuration = noHolidayDays(data['T0'][0:5]+'01-01', data['T0'][0:5]+'12-31')


    # Initial value
    S = data['S']
    X = data['X']
    m = data['m']
    t = float(len(aliveDuration)) / len(yearDuration)
    t_ = float(aliveTradingDuration) / yearTradingDuration
    n = len(aliveDuration) * m 
    n_ = aliveTradingDuration * m 
    ndiff = n - n_
    print 'n', n
    s = data['s'] / 100  # convert from percentage to decimal
    
    r = data['r'] / 100
    u = exp(s * sqrt(t_ / n_))
    d = 1 / u  # d = exp(-s * sqrt(t / n))
    r_ = r * t / n
    inR = exp(r_)
    p = (inR - d) / (u - d)  # Risk-neutral P

    # America put
    # Initialize Value at time t
    totalHper = m * (holidayBefore(aliveDuration[0], aliveDuration[-1]))
    print '--totalHper', totalHper
    choose = n-totalHper 
    print '--choose1', choose

    PutValueFlow = [max(X - (S * (u ** (choose-i)) * (d ** i) * (inR ** totalHper)), 0) for i in range(choose+1)]
    CallValueFlow = [max((S * (u ** (choose-i)) * (d ** i) * (inR ** totalHper)) - X, 0) for i in range(choose+1)]

    # Run backward to time 0
    for index, day in enumerate(aliveDuration[::-1]):
        for day_period in reversed(range(m)):
            period = (len(aliveDuration) - index - 1) * m + day_period
            hper = m * holidayBefore(aliveDuration[0], day) 

            if day.weekday() < 5:  # Weekday

                # Payoff of early exercise
                choose = period - hper
                PutEarlyExercise = [max(X - (S * (u ** (choose-i)) * (d ** i) *  
                                   (inR ** hper)), 0) for i in range(choose+1)]
                CallEarlyExercise = [max((S * (u ** (choose-i)) * (d ** i) * 
                                    ( inR ** hper)) - X, 0) for i in range(choose+1)]

                # Continuation value
                PutValueFlow = [((p * PutValueFlow[i] + (1-p) * PutValueFlow[i+1]) / inR) for i in range(choose+1)]
                CallValueFlow = [((p * CallValueFlow[i] + (1-p) * CallValueFlow[i+1]) / inR) for i in range(choose+1)]

                # Find the larger value
                if (((day + datetime.timedelta(-1)) in exercisableDuration) and day_period == 0 \
                      and (day + datetime.timedelta(-1)).weekday() < 5 ):
                    PutValueFlow = [max(PutEarlyExercise[i], PutValueFlow[i]) for i in range(len(PutValueFlow))]
                    CallValueFlow = [max(CallEarlyExercise[i], CallValueFlow[i]) for i in range(len(CallValueFlow))]

            else:  # Holiday
                PutValueFlow = [ (PutValueFlow[i] / inR) for i in range(len(PutValueFlow))]
                CallValueFlow = [ (CallValueFlow[i] / inR) for i in range(len(CallValueFlow))]

                if (day_period == 0 and \
                    ((day + datetime.timedelta(-1)) in exercisableDuration)) and \
                    ((day + datetime.timedelta(-1)).weekday() < 5):
                    choose = period-hper
                    PutEarlyExercise = [max(X - (S * (u ** (choose-i)) * (d ** i) *  
                                       (inR ** hper)), 0) for i in range(choose+1)]
                    CallEarlyExercise = [max((S * (u ** (choose-i)) * (d ** i) *  
                                        (inR ** hper)) - X, 0) for i in range(choose+1)]

                    PutValueFlow = [max(PutEarlyExercise[i], PutValueFlow[i]) for i in range(len(PutValueFlow))]
                    CallValueFlow = [max(CallEarlyExercise[i], CallValueFlow[i]) for i in range(len(CallValueFlow))]
        #print PutValueFlow

    # Output Information
    outputs = [ ('Bermuda Call', str(CallValueFlow[0])), ('Bermuda Put', str(PutValueFlow[0]))]

    # Aligned output
    print "S=%r, X=%r, s=%r%%, t=%r, n=%r, r=%r %%:" % (S, X, data['s'], t, n, data['r'])
    for output in outputs:
        print "- {item:13}: {value[0]:>4}.{value[1]:<12}".format(
              item=output[0], value=output[1].split('.') if '.' in output[1] else (output[1], '0'))


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
        print ''
        print 'Answer: The call price is about 8.4471, and the put price is about 3.4471.' 
        print 'Suppose we have the same parameters as above except that r = 10%.' 
        print 'Then the call price is about 9.4205, and the put price is about 2.9370'
    else:
        print 'This requires an input file.  Please select one from the data \
               directory. (e.g. python HW3.py ./data)'
