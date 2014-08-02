#!/usr/bin/python

"""
Parses a .gpx file into a path
"""

import geography
import xml.etree.ElementTree as ET
import time
import iso8601 #Not part of default install.

"""
This is the heavy lifting. Takes a dpx trkpt element that contains
a location, and returns a geography.Location object
"""
def trkptToLocation(pt):
    lat=None
    lon=None
    ele=0.0
    timestring=None
    timestamp=None
    attribs=pt.attrib
    #Lat and Lon are attributes
    for attrib in attribs.keys():
        if attrib=='lat':
            lat=attribs[attrib]
        if attrib=='lon':
            lon=attribs[attrib]
    #elevation and timestamp are subelements
    for c in pt.iter():
        tag=trimTag(c.tag)
        val=c.text
        if tag=='ele':
            ele=val
        if tag=='time':
            timestring=val
    if timestring != None:
        timestamp = iso8601.parse_date(timestring)
    loc=geography.Location(float(lat), float(lon), float(ele), timestamp)
    return loc

"""Trim leading namespace from tag
'{http://www.topografix.com/GPX/1/1}gpx' -> 'gpx' """ 
def trimTag(tag):
    return tag.split('}')[-1]

"""gpx is a string containing the gpx xml. Returns a geography.Path."""
def gpxToPath(gpx):
    path=geography.Path()
    it=ET.fromstring(gpx).iter()
    for child in it:
        t=trimTag(child.tag)
        if t == "trkpt":
            pt=trkptToLocation(child)
            path.append(pt)
    return path

"""Load a GPX file and turn it ito a path"""
def loadFile(fileName):
    return gpxToPath(open(fileName).read())

#######################Unit tests#################
import unittest

class TestTag(unittest.TestCase):
    def testTrimTag(self):
        self.assertEqual(trimTag(''), '')
        self.assertEqual(trimTag('abc'), 'abc')
        self.assertEqual(trimTag('}'), '')
        self.assertEqual(trimTag('}abc'), 'abc')
        self.assertEqual(trimTag(
            '{http://www.topografix.com/GPX/1/1}gpx'), 
            'gpx')

if __name__=="__main__":
    unittest.main()
