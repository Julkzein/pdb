# -*- coding: utf-8 -*-
"""
Created on Tue Feb 25 09:43:43 2025

@author: Samuel
"""

try:
    from Activity_cleaned import ActivityData, Activity
except ImportError:
    from Activity import ActivityData, Activity


class Library:
    def __init__(self, nameOfFile):
        with open(nameOfFile) as inputFile:
            data = inputFile.readlines()
            data = data[1:] #removing the headline

            self.liste = []
            idx = 0
            for line in data:
                self.liste.append(ActivityData(line.strip(), idx))
                idx += 1
            
    def __str__(self):
        res = ""
        for val in self.liste:
            res += str(val) + "\n"
        return res
    
    def getLength(self):
        return len(self.liste)

    def listeActData(self):
        return self.liste
    
    def getActData(self, number):
        if len(self.liste) < number:
            print("Error in getAct,", number, "out of range")
        return self.liste[number]
    
def tests():
    print("testing Activities")
    print("See file InstantiatedAct.py instead")
if __name__=="__main__":
    tests()