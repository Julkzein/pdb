# -*- coding: utf-8 -*-
"""
Created on Tue Feb 25 09:43:43 2025

@author: Samuel
"""


import math as m
import params as p

def linInterp(mi, ma, val):
    # gives the only value lambda such that mi + lambda * (ma - mi) = val
    if (ma-mi) < 0.0000001:
        if 0.0000001 < abs(mi - val):
            print("ERROR - linInterp: val != mi while ma != mi")
        return 0
    return (val - mi)/(ma-mi)

class pVal:
    # Each pVal is a tuple of values, normally ranging from 0 to 1 but the code does not restricts this.
    # The programm works ONLY if all pValues haves the same exact number of dimensions.
    
    def __init__(self, tupl):
        # Default init takes a tuple of floats.
        self.v = tupl

    @classmethod
    def fromString(cls, string):
        # Special init takes a string representing a tuple of floats without any spaces.
        return cls(tuple([float(val) for val in string.strip("()").split(";")]))

    def __str__(self):
        return p.FORMAT_PVAL.format(self.toString())
    
    def toString(self):
        # Returns a string representation which is ROUNDED.
        rounded = tuple(map(lambda x: round(x, 3), self.v))
        return str(rounded)
    
    def needToReach(self, other):
        """
        Imagine a class having current p-situation of self.
        If we teach them an activity having a p-condition of other, two cases can happen.
        1. The p-situation is further (in all directions) than the p-condition
            (then the course can start immediatly)
        2. There is a direction where the p-situation is below the p-condition
            (then there is some developpement to do before starting this course)
        
        needToReach returns the p-situation of the class after having done this work (if nec.).
        Hence we have the following requirements and guarantees:
            self  < self.needToReach(other) (the class can only grow during work)
            other < self.needToReach(other) (the class has reached the p-cond of the course)
        """
        maximums = [max(self.v[idx], other.v[idx]) for idx in range(len(self.v))]
        return pVal(maximums)
    
    def plus(self, effect):
        res = [self.v[idx] + effect.v[idx] for idx in range(len(self.v))]
        return pVal(res)
    
    def minus(self, effect):
        res = [self.v[idx] - effect.v[idx] for idx in range(len(self.v))]
        return pVal(res)
    
    def times(self, val):
        res = [self.v[idx]*val for idx in range(len(self.v))]
        return pVal(res)
    
    def isPast(self, other):
        # self.isPast(other) returns True iff self is at least as advanced as other
        # (in all directions)  i.e. other[i] <= self[i] for all i.
        # NOTE: start.isPast(pcond) == True implies that a class currently at
        # start can already start learning pcond without any more work.
        # self.isPast(other) =!= not other.isPast(self)
        for i in range(len(self.v)):
            if self.v[i]+p.PRECISION < other.v[i]:
                return False
        return True

    def distance2(self, other):
        # Returns the Euclidean distance squared
        som = 0
        for i in range(len(self.v)):
            som += (self.v[i] - other.v[i])**2
        return som
    
    def distance(self, other):
        # Returns the Euclidean distance
        return m.sqrt(self.distance2(other))
    
    def distance2_onlyForward(self, other):
        # Returns the Euclidean distance squared
        # from self to the nearest point past other.
        som = 0
        for i in range(len(self.v)):
            if self.v[i] < other.v[i]:
                som += (self.v[i] - other.v[i])**2
        return som
    
    def distance_onlyForward(self, other):
        # Returns the Euclidean distance
        return m.sqrt(self.distance2_onlyForward(other))
    
    
class InterPVal:
    def __init__(self, pMin, pMax, tMin, tMax, tDef):
        self.pMin = pMin
        # self.pDelta = pMax - pMin
        self.pDelta = pMax.minus(pMin)
        self.tMin = tMin
        self.tMax = tMax
        self.tDef = tDef
        self.defaultPEffect = None
        
        
    def __str__(self):
        if self.tMin == self.tMax:
            return str(self.default())
        return p.FORMAT_PVAL.format("["+self.default().toString()[1:-1]+"]")
        
        
    @classmethod
    def fromStrings(cls, pMin, pMax, tMin, tMax, tDef):
        # Special init takes a string representing a tuple of floats without any spaces.
        return cls(pVal.fromString(pMin), pVal.fromString(pMax), tMin, tMax, tDef)

    
    def get(self, t):
        # Returns the p-effect corresponding to the time t if t in the accepted frame.
        if t < self.tMin or self.tMax < t:
            raise ValueError('Error - InterPVal: time out of Bound')
        #return self.pMin + self.pDelta * lambda
        return self.pMin.plus( self.pDelta.times(linInterp(self.tMin, self.tMax, t)) )
    
    def default(self):
        # Returns the p-effect corresponding to the default time.
        if self.defaultPEffect is None:
            # Only compute it once
            self.defaultPEffect = self.get(self.tDef)
        return self.defaultPEffect
        


def tests():
    print("testing pValues")
    print("no test yet implemented")
    
if __name__=="__main__":
    tests()