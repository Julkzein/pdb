# -*- coding: utf-8 -*-
"""
Created on Tue Feb 25 09:43:43 2025

@author: Samuel
"""

from pValues import pVal
from pValues import InterPVal
from PyQt6.QtCore import QObject, pyqtProperty, pyqtSignal
from Plane import intFromPlane
from Plane import planeFromInt, descriptionFromInt

import params as p

class ActivityData:
    def __init__(self, line:str, idx:int):
        data = line.split(',')

        # idx: Index of the activity in the library
        self.idx = idx
        
        # str: Name of the activity
        self.name = data[0]
        
        # pVal: The p-condition from which the activity can start
        self.pcond = pVal.fromString(data[1])
        
        if data[6] != '':
            # bool: True if the time can be interpolated
            self.canChangeTime = True

            minEffect = data[2]
            maxEffect = data[4]

            # int: minimum time
            self.minT = int(data[3])

            # int: maximum time
            self.maxT = int(data[5])

            # int: default time
            self.defT = int(data[6])
            
        else:
            # If no default time is given, we consider min=max=default with only max given.
            self.canChangeTime = False
            minEffect = data[4]
            self.minT = int(data[5])
            maxEffect = data[4]
            self.maxT = int(data[5])
            self.defT = int(data[5])

        
        # InterPVal: The p-effect dependent on the time decided
        self.peffect = InterPVal.fromStrings(minEffect, maxEffect, self.minT, self.maxT, self.defT)

        # int: The max number of repetition recommended
        self.maxRepetition = int(data[7])

        # int: index representing the plane
        self.defPlane = intFromPlane(data[8])
    
    def toString(self, details = False):
        string = "Act " + p.FORMAT_NAME.format(self.name) + " {"
        string += "from " + str(self.pcond)
        string += " +" + str(self.peffect)
        if details and self.canChangeTime:
            string += "\n time from " + p.FORMAT_TIME.format(str(self.minT)) + "'"
            string += " to " + p.FORMAT_TIME.format(str(self.maxT)) + "'"
        else:
            string += " in " + p.FORMAT_TIME.format(str(self.defT)) + "'"
        string += " and " + str(self.maxRepetition) + " max rep."
        string += " on " + planeFromInt(self.defPlane)
        string += "}"
        return string
    
    def __repr__(self):
        return self.toString(False)
    
    def __getstate__(self):
        # https://stackoverflow.com/questions/1939058/simple-example-of-use-of-setstate-and-getstate
        out = self.__dict__.copy()
        out.pop("QTObjectNotVisibleFromPickle", None)
        return out
    
    def what_from(self, start, notDefTime = None):
        would_start = start.needToReach(self.pcond)
        if notDefTime == None:
            would_end = would_start.plus(self.peffect.default())
            time = self.defT
        else:
            would_end = would_start.plus(self.peffect.get(notDefTime))
            time = notDefTime
        return would_start, would_end, time
    
    def getQtObject(self):
        # Returns a PyQt6 object to be used in the GUI
        self.QTObjectNotVisibleFromPickle = Activity(self)
        return self.QTObjectNotVisibleFromPickle
    

class Activity(QObject):
    activityChangeSignal = pyqtSignal()

    def __init__(self, data:ActivityData):
        super().__init__()
        self.data = data

    @pyqtProperty(str, notify=activityChangeSignal)
    def label(self):
        return self.data.name
    
    @pyqtProperty(int, notify=activityChangeSignal)
    def defTime(self):
        return self.data.defT
    
    @pyqtProperty(str, notify=activityChangeSignal)
    def planeDescription(self):
        return descriptionFromInt(self.data.defPlane)
        
    
    
def tests():
    print("testing Activities")
    print("See file InstantiatedAct.py instead")
    
if __name__=="__main__":
    tests()