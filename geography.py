#!/usr/bin/python

"""Geography - assumes we're on Earth"""
RADIUS = 6371000 # Earth, in metres
DISTANCE_ERROR = 0.001 #1 millimeter

from math import sin, cos, tan, atan2, degrees, radians, sqrt, pi
from pairfold import pairfoldp, pairs
import datetime

#Exceptions
class RangeException(Exception):
    pass

#check value is in range, throw if not
def checkRange(val, minimum, maximum):
    if minimum <= val <= maximum:
        pass
    else:
        raise RangeException("%.2f not between %.2f and %.2f" 
                             % (val, minimum, maximum))
def sq(x):
    return x * x

"""Use haversine to calc distance between two points"""
def distance(p1,p2):
    delta_lat = p1.getLat() - p2.getLat()
    delta_lon = p1.getLon() - p2.getLon()
    haversine = (sq(sin (delta_lat/2.0)) +
                 cos(p1.getLat()) * cos (p2.getLat()) *
                 (sq(sin(delta_lon/2.0))))
    angle = 2 * atan2(sqrt(haversine), sqrt(1-haversine))
    return RADIUS * angle

"""p is a tuple of two Location objects"""
def pairDistance(p):
    return distance(p[0], p[1])

"""Length of an ordered set of locations"""
def pathLength(p):
    return pairfoldp(distance, p)

"""Altitude diff helpers"""
def altDiff(p1,p2):
    return p2.alt - p1.alt

def posAltDiff(p1,p2):
    return max(altDiff(p1,p2), 0.0)

def negAltDiff(p1,p2):
    return min(altDiff(p1,p2), 0.0)

"""A time/distance split"""
class Split:
    def __init__(self, time, distance):
        self.time = time
        self.distance = distance

"""A location on the surface of the earth"""
class Location:
    """Lat and Long stored as radians"""
    def __init__(self, lat, lon, alt=0.0, time=None):
        try: 
            checkRange(lat, -90.0, +90.0)
            checkRange(lon, -180.0, +180.0)
        except RangeException as r:
            raise
        self.lat=radians(lat)
        self.lon=radians(lon)
        self.alt=alt
        self.time=time
    def getLat(self):
        return self.lat
    def getLon(self):
        return self.lon
    def latHemi(self):
        if self.lat > 0:
            return "N"
        else:
            return "S"
    def lonHemi(self):
        if self.lon > 0:
            return "E"
        else:
            return "W"
    def __unicode__(self):
        if self.time == None:
            timeString = ""
        else:
            timeString=str(self.time)
        return "Lat:%2.4f%s Lon:%3.4f%s Alt: %.1f %s" % (degrees(self.lat), 
                                                        self.latHemi(),                                                                    degrees(self.lon),
                                                        self.lonHemi(),
                                                        self.alt,
                                                        timeString)
    def __str__(self):
        return unicode(self).encode('utf-8')
    def distance(self,p):
        return distance(self, p)

    def __eq__(self, p):
        return self.distance(p) < DISTANCE_ERROR

    def __ne__(self, p):
        return not (self.__eq__(p))

"""An ordered set of locations"""
class Path():
    def __init__(self, p=None):
        if p==None:
            self.path=[]
            self._splits=[]
        else:
            self.path=p
            self._splits=self.calcSplits()
    def getPath(self):
        return self.path
    def append(self,p):
        self.path.append(p)
    def __len__(self):
        return len(self.path)
    def __getitem__(self, n):
        return self.path[n]

    """Cumulative time/distances"""
    def calcSplits(self):
        splits=[]
        totTime = datetime.timedelta(0)
        totDist = 0
        locPairs = pairs(self.path)
        for p in locPairs:
            totTime = totTime + (p[1].time - p[0].time)
            totDist = totDist + distance(p[1], p[0])
            splits.append(Split(totTime, totDist))
        return splits

    def splits(self): #Might memoize this
        return self.calcSplits()
    
    """Given a distance, return the first time
    that distance is exceeded"""
    def splitTime(self, distance):
        ss=self.splits()
        for s in ss:
            if s.distance >= distance:
                return s.time
        #No split found
        return 0

    """Return a list of split times at kms"""
    def distSplits(self, metres=1000):
        kmSplits=[]
        for km in range(1, int(self.pathLength()/metres)):
            kmSplits.append(self.splitTime(km * metres))
        return kmSplits

    def distSplitsAbsolute(self, metres=1000):
        kmSplitsAbs=[]
        lastTime=datetime.timedelta()
        for km in range(1, int(self.pathLength()/metres)):
            st=self.splitTime(km * metres)
            kmSplitsAbs.append(st - lastTime)
            lastTime=st
        return kmSplitsAbs

    """How far did we go?"""
    def pathLength(self):
        return pathLength(self.path)

    """How far did we climb?"""
    def climb(self):
        return pairfoldp(posAltDiff, self.path)

    """How far did we descend?"""
    def descent(self):
        return pairfoldp(negAltDiff, self.path)

""" Unit Tests """
import unittest

class TestLocations(unittest.TestCase):
    def setUp(self):
        self.o1 =Location(0.0,0.0,0.0)
        self.o2 =Location(0.0,0.0,1.0)
        self.np1=Location(90.0,0.0)
        self.np2=Location(90.0,90.0)
        self.sp =Location(-90, 0.0)
        self.br =Location(-27.505, 152.970)
    def testRanges(self):
        with self.assertRaises(RangeException):
            a=Location(0.0,-180.1)
        with self.assertRaises(RangeException):
            b=Location(0.0,180.1)
        with self.assertRaises(RangeException):
            c=Location(90.1,0.0)
        with self.assertRaises(RangeException):
            d=Location(-90.1,0.0)
        with self.assertRaises(RangeException):
            e=Location(1000.0,1000.0)

    def testEquality(self):
        self.assertTrue(self.o1==self.o1)
        self.assertTrue(self.o1==self.o2)
        self.assertFalse(self.np1==self.sp)

    def testDistances(self):
        self.assertTrue(self.o1.distance(self.o1)==0)
        self.assertTrue(self.np1.distance(self.np2) < DISTANCE_ERROR)
        self.assertTrue(self.sp.distance(self.np1)== RADIUS * pi)
    def testAltDiff(self):
        self.assertEqual(altDiff(self.o1,self.o1), 0.0)
        self.assertEqual(altDiff(self.o1,self.o2), 1.0)
        self.assertEqual(altDiff(self.o2,self.o1), -1.0)
    def testPosAltDiff(self):
        self.assertEqual(posAltDiff(self.o1,self.o1), 0.0)
        self.assertEqual(posAltDiff(self.o1,self.o2), 1.0)
        self.assertEqual(posAltDiff(self.o2,self.o1), 0.0)
    def testNegAltDiff(self):
        self.assertEqual(negAltDiff(self.o1,self.o1), 0.0)
        self.assertEqual(negAltDiff(self.o1,self.o2), 0.0)
        self.assertEqual(negAltDiff(self.o2,self.o1), -1.0)

class TestPaths(unittest.TestCase):
    def setUp(self):
        self.loc1 = Location(-27.505, 152.970, 10.0) #Home
        self.loc2 = Location(-27.467, 153.027, 20.0) #Work
        self.nullPath = Path([])
        self.commutePath=Path([self.loc1,self.loc2,self.loc1])
        c1=Location(0.0,0.0,0.0)
        c2=Location(0.1,0.0,10.0)
        c3=Location(0.2,0.0,20.0)
        c4=Location(0.3,0.0,10.0)
        c5=Location(0.4,0.0,0.0)
        self.hillPath=Path([c1,c2,c3,c4,c5])

    def testDistances(self):
        self.assertTrue(self.nullPath.pathLength() < DISTANCE_ERROR)
        commuteLength = self.commutePath.pathLength()
        d1=distance(self.loc1, self.loc2)
        self.assertTrue(commuteLength == (2 * d1))
    
    def testPairDistance(self):
        self.assertEqual(pairDistance((self.loc1, self.loc2)),
                         distance(loc1,loc2))

    def testClimbs(self):
        self.assertEqual(self.nullPath.climb(), 0.0)
        self.assertEqual(self.commutePath.climb(), 10.0)
        self.assertEqual(self.nullPath.climb(), 0.0)
        self.assertEqual(self.hillPath.climb(), 20.0)
        self.assertEqual(self.hillPath.descent(), -20.0)

if __name__== "__main__":
    unittest.main()
