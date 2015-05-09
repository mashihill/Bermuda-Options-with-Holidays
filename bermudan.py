#!/usr/bin/env python
# encoding: utf-8

from __future__ import division
from math import *
from collections import namedtuple
import scipy.stats
import datetime

class BermudanOption:

    CallValueFlow = []
    PutValueFlow = []

    def __init__(self, S, X, s, T0, T1, T2, T3, m, r):
        self._S = S
        self._X = X
        self._s = s / 100  # from percentage to decimal
        self._T0 = datetime.date(*[int(x) for x in T0.split('-')])
        self._T1 = datetime.date(*[int(x) for x in T1.split('-')])
        self._T2 = datetime.date(*[int(x) for x in T2.split('-')])
        self._T3 = datetime.date(*[int(x) for x in T3.split('-')])
        self._m = m
        self._r = r / 100

    def _build(self):
        self._n_calendar = self.daysBetween(self._T0, self._T3, 1) * self._m
        self._n_trading = self.daysBetween(self._T0, self._T3, 0) * self._m
        # BAD
        self._t_calendar = self._n_calendar / self._m / self.daysBetween(datetime.datetime(2015, 1, 1), datetime.datetime(2015, 12, 31), 1)
        self._t_trading = self._n_trading / self._m / self.daysBetween(datetime.datetime(2015, 1, 1), datetime.datetime(2015, 12, 31), 0)

        print self._n_calendar, self._n_trading, self._t_calendar, self._t_trading

        self._u = exp(self._s * sqrt(self._t_trading / self._n_trading))
        self._d = 1 / self._u
        self._R = exp(self._r * self._t_calendar / self._n_calendar)
        self._p = (self._R - self._d) / (self._u - self._d)


        holidayPeriods = self._n_calendar - self._n_trading
        Period = namedtuple("Period", ["Date", "Period", "Exercisable", "PeriodInDay", \
                            "holidayPeriods", "tradingPeriods"])
        matureperiod = Period(self._T1, self._n_calendar, 1, self._m, holidayPeriods, self._n_trading)
        #print matureperiod
        self.PutValueFlow = self.exercise(matureperiod, 'p')
        self.CallValueFlow = self.exercise(matureperiod, 'c')

        #print self.PutValueFlow
        #print self.CallValueFlow


    def price(self):
        self._build()
        for p in reversed(list(self.periodGenerator(self._T0, self._T1, self._T2, self._T3, self._m))):
            if p.Date.weekday() in [5, 6]:
                self.PutValueFlow = [self.PutValueFlow[i] / self._R for i in range(len(self.PutValueFlow))]
                self.CallValueFlow = [self.CallValueFlow[i] / self._R for i in range(len(self.CallValueFlow))]
                if p.Exercisable == 1:
                    PutExercise = self.exercise(p, 'p')
                    CallExercise = self.exercise(p, 'c')
                    self.PutValueFlow = [max(self.PutValueFlow[i], PutExercise[i]) for i in range(len(PutExercise))]
                    self.CallValueFlow = [max(self.CallValueFlow[i], CallExercise[i]) for i in range(len(CallExercise))]
            else:
                self.PutValueFlow = self.conti(self.PutValueFlow)
                self.CallValueFlow = self.conti(self.CallValueFlow)
                if p.Exercisable == 1:
                    PutExercise = self.exercise(p, 'p')
                    CallExercise = self.exercise(p, 'c')
                    self.PutValueFlow = [max(self.PutValueFlow[i], PutExercise[i]) for i in range(len(PutExercise))]
                    self.CallValueFlow = [max(self.CallValueFlow[i], CallExercise[i]) for i in range(len(CallExercise))]
        print 'put: ', self.PutValueFlow[0], 'call: ', self.CallValueFlow[0]

    def daysBetween(self, startDate, endDate, includeHolidays):
        daygenerator = (startDate + datetime.timedelta(x) for x in xrange((endDate - startDate).days + 1))
        if includeHolidays:
            return sum(1 for day in daygenerator)
        else:
            return sum(1 for day in daygenerator if day.weekday() < 5)

    def periodGenerator(self, startDate, endDate, exStart, exEnd, periodsPerDay):
        Period = namedtuple("Period", ["Date", "Period", "Exercisable", "PeriodInDay",
                            "holidayPeriods", "tradingPeriods", "IsHoliday"])
        holiday = 0
        for day in range((endDate - startDate).days+1):
            for pd in range(periodsPerDay):
                ish = 0
                today = startDate + datetime.timedelta(day)
                period = day * periodsPerDay + pd
                exercisable = 0
                if today.weekday() in [5,6]:
                    ish = 1
                if (today+datetime.timedelta(-1)) <= exEnd and (today+datetime.timedelta(-1)) >= exStart:
                    if pd == 0:
                        if today.weekday() not in [0, 6]:
                            exercisable = 1
                yield Period(today, period, exercisable, pd, holiday, period - holiday, ish)
                if today.weekday() in [5, 6]:
                    holiday += 1

    def exercise(self, Period, optionType):
        if optionType == 'p':
            return [max(self._X - (self._S * (self._u ** (Period.tradingPeriods-i)) * (self._d ** i) * \
                    (self._R ** Period.holidayPeriods)), 0) for i in range(Period.tradingPeriods+1)]
        elif optionType == 'c':
            return [max((self._S * (self._u ** (Period.tradingPeriods-i)) * (self._d ** i) * \
                    (self._R ** Period.holidayPeriods)) - self._X, 0) for i in range(Period.tradingPeriods+1)]

    def conti(self, ValueFlow):
        return [((self._p * ValueFlow[i] + (1-self._p) * ValueFlow[i+1]) / self._R) \
                for i in range(len(ValueFlow)-1)]


def bermuda(data):

    # Initial value
    inputdata = [data[i] for i in ['S', 'X', 's', 'T0', 'T1', 'T2', 'T3', 'm', 'r']]
    bermudaOption = BermudanOption(*inputdata)
    bermudaOption.price()

import sys
import json
if __name__ == '__main__':
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location) as data_file:
            data = json.load(data_file)
        for test in data:
            bermuda(test)
    else:
        print 'This requires an input file.  Please select one from the data \
               directory. (e.g. python HW3.py ./data)'
