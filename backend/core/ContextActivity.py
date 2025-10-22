# -*- coding: utf-8 -*-
"""
Created on Tue Feb 25 09:43:43 2025

@author: Samuel
"""

from Activity import ActivityData
from PyQt6.QtCore import QObject, pyqtProperty, pyqtSignal

class FlagContainer(QObject):
    def __init__(self, list):
        super().__init__()
        self.exhausted = "tooM" in list
        self.tooLong = "long" in list
        self.noProgress = "noProg" in list

    flagChangeSignal = pyqtSignal()
    
    @pyqtProperty(bool, notify=flagChangeSignal)
    def isExhausted(self):
        return self.exhausted
    
    @pyqtProperty(bool, notify=flagChangeSignal)
    def isTooLong(self):
        return self.tooLong
    
    @pyqtProperty(bool, notify=flagChangeSignal)
    def makesNoProgress(self):
        return self.noProgress
    
    def countFlags(self):
        som = 0
        if self.exhausted:
            som += 1
        if self.tooLong:
            som += 1
        return som
    
    def __repr__(self):
        return f"FlagContainer(exhausted={self.exhausted}, tooLong={self.tooLong}, makesNoProgress={self.noProgress})"



class ContextActivity(QObject):
    contextActivityChangeSignal = pyqtSignal()

    def __init__(self, activity : ActivityData, score:float, flags):
        super().__init__()
        self.myActData = activity
        self.myScore = score
        self.myFlags = FlagContainer(flags)
        self.isBest = False #by default

    def __repr__(self):
        return f"ContextActivity({self.myActData.name}, {self.myScore}, {self.myFlags})"

    def countFlags(self):
        return self.myFlags.countFlags()
    
    def okeyToTake(self):
        return not self.myFlags.makesNoProgress
    
    @pyqtProperty(QObject, notify=contextActivityChangeSignal)
    def activity(self):
        return self.myActData.getQtObject()
    
    @pyqtProperty(QObject, notify=contextActivityChangeSignal)
    def flags(self):
        return self.myFlags
    

    @pyqtProperty(bool, notify=contextActivityChangeSignal)
    def hasScore(self):
        return (self.myScore != None)
    
    @pyqtProperty(float, notify=contextActivityChangeSignal)
    def score(self):
        return self.myScore
    
    @pyqtProperty(bool, notify=contextActivityChangeSignal)
    def isRecommended(self):
        return self.isBest


    
def tests():
    print("No tests for ContextActivity")
    
if __name__=="__main__":
    tests()