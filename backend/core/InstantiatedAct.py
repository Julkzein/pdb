# -*- coding: utf-8 -*-
"""
Created on Tue Feb 25 09:43:43 2025

@author: Samuel

Handles the instantiation of an activity for a given pState as given by the place in the lesson.

"""

from Activity import ActivityData
from pValues import pVal
from Library import Library
from Plane import planeFromInt, descriptionFromInt

import params as p
from PyQt6.QtCore import QObject, pyqtProperty, pyqtSignal, pyqtSlot

class InstantiatedActData:
    def __init__(self, activityData:ActivityData, pstate):
        self.actData = activityData
        self.start, self.end, self.time = self.actData.what_from(pstate)
        self.plane_ = self.actData.defPlane
        self.startsAfter = 0 #default
    
    def __repr__(self):
        string = "InstAct of " + p.FORMAT_NAME.format(self.actData.name) + " from "
        string += str(self.start) + " to " + str(self.end)
        string += "(" + str(self.time) + "')"
        string += " on " + planeFromInt(self.plane_)
        return string
    
    def __getstate__(self):
        # https://stackoverflow.com/questions/1939058/simple-example-of-use-of-setstate-and-getstate
        out = self.__dict__.copy()
        out.pop("QTObjectNotVisibleFromPickle", None)
        return out
    
    def adjust(self, pNew = None, notDefTime = None):
        # Modify the start and end pValues given a new starting-position
        if pNew is None: # This happens when only the duration of the activity is changed.
            pNew = self.start
        self.start, self.end, self.time = self.actData.what_from(pNew, notDefTime)

    def getQtObject(self):
        # Returns a PyQt6 object to be used in the GUI
        self.QTObjectNotVisibleFromPickle = InstantiatedAct(self)
        return self.QTObjectNotVisibleFromPickle

class InstantiatedAct(QObject):
    instActChangeSignal = pyqtSignal()

    def __init__(self, data:InstantiatedActData):
        super().__init__()
        self.data = data
    
    def __repr__(self):
        return str(self.data)
    
    @pyqtProperty(int, notify=instActChangeSignal)
    def myTime(self):
        return self.data.time
    
    @pyqtProperty(int, notify=instActChangeSignal)
    def startsAfter(self):
        return self.data.startsAfter
    
    @pyqtProperty(int, notify=instActChangeSignal)
    def plane(self):
        return self.data.plane_
    
    @pyqtProperty(str, notify=instActChangeSignal)
    def planeDescription(self):
        return descriptionFromInt(self.data.plane_)
    
    @pyqtProperty(str, notify=instActChangeSignal)
    def label(self):
        return self.data.actData.name
    
    @pyqtProperty(bool, notify=instActChangeSignal)
    def canChangeTime(self):
        return self.data.actData.canChangeTime

    @pyqtProperty(int, notify=instActChangeSignal)
    def minTime(self):
        return self.data.actData.minT

    @pyqtProperty(int, notify=instActChangeSignal)
    def maxTime(self):
        return self.data.actData.maxT
    

    # SLOTS
    @pyqtSlot(int)
    def setTime(self, newTime):
        self.data.time = newTime

    @pyqtSlot(int)
    def setPlane(self, newPlane):
        self.data.plane_ = newPlane
    
def tests():
    print("testing Activities and Librairies")
    myLib = Library("inputData/interpolation_2D_library.csv")
    print(myLib)
        
        
    print("We start by instantiating all activities of the library for students in a state", end = ' ')
    startingPValue = pVal((0.0, 0.0))
    print(startingPValue)
    liste_one = [InstantiatedActData(myLib.getActData(i), startingPValue) for i in range(len(myLib.liste))]
    [print(liste_one[i]) for i in range(len(liste_one))]
    
    print()
    print("Then, we update each of those instantiated activities to start at", end = ' ')
    adjustPValue = pVal((0.15, 0.4))
    print(adjustPValue)
    print("This represents the teacher adding an activity before them.")
    for act in liste_one:
        act.adjust(adjustPValue)
        print(act)
            
    
    print()
    print("The library if all were instantiated for students in a state", end = ' ')
    startingPValue = pVal((0.3, 0.3))
    print(startingPValue)
    liste_two = [InstantiatedActData(myLib.getActData(i), startingPValue) for i in range(len(myLib.liste))]
    [print(liste_two[i]) for i in range(len(liste_two))]
    
if __name__=="__main__":
    tests()