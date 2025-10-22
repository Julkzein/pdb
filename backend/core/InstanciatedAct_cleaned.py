# -*- coding: utf-8 -*-
"""
InstantiatedAct without PyQt6 dependencies
Modified for web backend usage

Handles the instantiation of an activity for a given pState as given by the place in the lesson.
"""

try:
    from Activity_cleaned import ActivityData
except ImportError:
    from Activity import ActivityData
from pValues import pVal
from Library import Library
from Plane import planeFromInt, descriptionFromInt
import params as p

class InstantiatedActData:
    def __init__(self, activityData: ActivityData, pstate):
        self.actData = activityData
        self.start, self.end, self.time = self.actData.what_from(pstate)
        self.plane_ = self.actData.defPlane
        self.startsAfter = 0  # default
    
    def __repr__(self):
        string = "InstAct of " + p.FORMAT_NAME.format(self.actData.name) + " from "
        string += str(self.start) + " to " + str(self.end)
        string += "(" + str(self.time) + "')"
        string += " on " + planeFromInt(self.plane_)
        return string
    
    def __getstate__(self):
        out = self.__dict__.copy()
        out.pop("QTObjectNotVisibleFromPickle", None)
        return out
    
    def adjust(self, pNew=None, notDefTime=None):
        """Modify the start and end pValues given a new starting-position"""
        if pNew is None:  # This happens when only the duration of the activity is changed.
            pNew = self.start
        self.start, self.end, self.time = self.actData.what_from(pNew, notDefTime)
    
    def setTime(self, newTime):
        """Set the time for this activity"""
        self.time = newTime
    
    def setPlane(self, newPlane):
        """Set the plane for this activity"""
        self.plane_ = newPlane
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'name': self.actData.name,
            'time': self.time,
            'startsAfter': self.startsAfter,
            'plane': self.plane_,
            'planeDescription': descriptionFromInt(self.plane_),
            'canChangeTime': self.actData.canChangeTime,
            'minTime': self.actData.minT,
            'maxTime': self.actData.maxT,
            'start': str(self.start),
            'end': str(self.end)
        }

# Alias for compatibility
InstantiatedActivity = InstantiatedActData
InstantiatedAct = InstantiatedActData

def tests():
    print("testing Activities and Libraries")
    myLib = Library("inputData/interpolation_2D_library.csv")
    print(myLib)
        
    print("We start by instantiating all activities of the library for students in a state", end=' ')
    startingPValue = pVal((0.0, 0.0))
    print(startingPValue)
    liste_one = [InstantiatedActData(myLib.getActData(i), startingPValue) for i in range(len(myLib.liste))]
    [print(liste_one[i]) for i in range(len(liste_one))]
    
    print()
    print("Then, we update each of those instantiated activities to start at", end=' ')
    adjustPValue = pVal((0.15, 0.4))
    print(adjustPValue)
    print("This represents the teacher adding an activity before them.")
    for act in liste_one:
        act.adjust(adjustPValue)
        print(act)
    
    print()
    print("The library if all were instantiated for students in a state", end=' ')
    startingPValue = pVal((0.3, 0.3))
    print(startingPValue)
    liste_two = [InstantiatedActData(myLib.getActData(i), startingPValue) for i in range(len(myLib.liste))]
    [print(liste_two[i]) for i in range(len(liste_two))]
    
if __name__ == "__main__":
    tests()