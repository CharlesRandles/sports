#!/usr/bin/python

"""
Consider a list of type [a] and a fn that reduces a->a->b
pairfold takes a list and a fn and applies the fn to each
pair in the list and accumulates the results by a given
function, starting with an initial value.
Haskell-speak:
(a->a->b)->[a]->(b->b)->b->b
"""

"""
Takes a list and returns a list of tuples of 
successive pairs. [1,2,3] -> [(1,2), (2,3)]
"""
def pairs(l):
    p=[]
    for i in range(len(l) - 1):
        p.append((l[i], l[i+1]))
    return p

"""
l is a list of type [a]
fn is a function of type a->a->b
acc in the accumulation function b->b->b
init is the initial value for the accumulator of type b
"""
def rec_pairfold(fn, l, acc, init):
    if len(l) < 2:
        return init
    return rec_pairfold(fn, l[1:], acc, acc(init, fn(l[0],l[1])))
#Damn. Has to be iterative - no tail rec optimisation
def pairfold(fn, l, acc, init):
    current=init
    for i in range(len(l)-1):
        current=acc(current, fn(l[i], l[i+1]))
    return current

"""Same as pairfold, but uses + and 0 for acc, init"""
def pairfoldp(fn,l):
    def plus(a,b): return a+b
    return pairfold(fn, l, plus, 0)

####Unit Tests

import unittest
import math

def sq(x): return x * x

def distance(a,b):
    return math.sqrt(sq(a.x-b.x) + sq(a.y-b.y))

class Point():
    def __init__(self, x, y):
        self.x=x
        self.y=y

class TestDistance(unittest.TestCase):
    def setUp(self):
        self.a=Point(0,0)
        self.b=Point(3,0)
        self.c=Point(0,4)
        self.d=Point(3,4)
    def testDistance(self):
        self.assertEqual(distance(self.a,self.a), 0.0)
        self.assertEqual(distance(self.a,self.b), 3.0)
        self.assertEqual(distance(self.a,self.c), 4.0)
        self.assertEqual(distance(self.a,self.d), 5.0)

class TestPairFold(unittest.TestCase):
    def setUp(self):
        self.empty=[]
        self.single=[Point(0,0)]
        self.double=[Point(0,0), Point(3.0,4.0)]
        self.many=[]
        for i in range(20):
            self.many.append(Point(i,0))
    def testPairFold(self):
        def plus(a,b): return a + b
        self.assertEqual(pairfold(distance, self.empty, plus, 0), 0.0)
        self.assertEqual(pairfold(distance, self.single, plus, 0), 0.0)
        self.assertEqual(pairfold(distance, self.double, plus, 0), 5.0)
        self.assertEqual(pairfold(distance, self.many, plus, 0), 19.0)
    def testRecPairFold(self):
        def plus(a,b): return a + b
        self.assertEqual(rec_pairfold(distance, self.empty, plus, 0), 0.0)
        self.assertEqual(rec_pairfold(distance, self.single, plus, 0), 0.0)
        self.assertEqual(rec_pairfold(distance, self.double, plus, 0), 5.0)
        self.assertEqual(rec_pairfold(distance, self.many, plus, 0), 19.0)

    def testPairFoldP(self):
        self.assertEqual(pairfoldp(distance, self.empty), 0.0)
        self.assertEqual(pairfoldp(distance, self.single), 0.0)
        self.assertEqual(pairfoldp(distance, self.double), 5.0)
        self.assertEqual(pairfoldp(distance, self.many), 19.0)

    def testPairs(self):
        self.assertEqual(pairs([]), [])
        self.assertEqual(pairs([1]), [])
        self.assertEqual(pairs([1,2]), [(1,2)])
        self.assertEqual(pairs([1,2,3]), [(1,2), (2,3)])

if __name__=="__main__":
    unittest.main()
    
