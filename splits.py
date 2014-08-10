#!/usr/bin/python

"""
Utilities for split times/distances
"""

import geography
import unittest
import datetime

"""Stores a single (distance, time) record """
class Split(object):
    def __init__(self, distance, time):
        self.distance = distance
        self.time = time

    def __unicode__(self):
        return unicode("Distance: %d\t\tTime: %s" % (int(self.distance),
                                                     str(self.time)))
    def __str__(self):
        return self.__unicode__()

"""Cumulative times and distances"""
class SplitTimes(object):
    def __init__(self, path, distance = 1000):
        self.splits=[]
        if len(path) < 2:
            #No splits for you!
            return
        for split in self.calcSplits(path, distance):
            self.splits.append(split)

    def calcSplits(self, path, distance):
        lastSplitDist=0.0
        lastSplitTime=datetime.timedelta(0)
        cumDist=0.0
        cumTime = datetime.timedelta(0)
        lastLoc = path[0]
        for loc in path[1:]:
            cumDist = cumDist + lastLoc.distance(loc)
            cumTime = cumTime + (loc.time - lastLoc.time)
            #Is it a split?
            if cumDist - lastSplitDist >= distance:
                s=Split(cumDist, cumTime - lastSplitTime)
                yield s
                lastSplitDist = cumDist
                lastSplitTime = cumTime
    def __getitem__(self, index):
        return self.splits[index]

#####Unit Tests####
class TestSplits(unittest.TestCase):
    def setUp(self):
        #Create a path
        heading = 0.0
        startTime = datetime.datetime(2014, 8, 8, 12, 19, 0)
        stepTime = 30 # seconds
        start=geography.Location(-23, 137, 20, startTime)
        self.path = geography.Path()
        p = start.copy()
        for i in range(100):
            self.path.append(p)
            p = p.copy()
            p.move(heading, 100 + i, stepTime)
            stepTime+=1
            heading += i
        print self.path.pathLength()

    def testSplits(self):
        l1=geography.Location(-23, 137)
        l2=l1.copy().move(45, 501)
        l3=l2.copy().move(30, 501)
        p=geography.Path([l1,l2,l3])
        s=SplitTimes(p)
        for ss in s:
            print ss
        t=SplitTimes(self.path)
        for tt in t:
            print tt

if __name__== "__main__":
    unittest.main()

