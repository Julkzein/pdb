# -*- coding: utf-8 -*-
"""
OrchestrationGraph without PyQt6 dependencies
Modified for web backend usage
"""

import sys
import os
import pickle
from typing import List, Optional, Dict, Any

from Library import Library
try:
    from InstantiatedAct_cleaned import InstantiatedActData, InstantiatedActivity
except ImportError:
    from InstantiatedAct import InstantiatedActData

try:
    from ContextActivity_cleaned import ContextActivity
except ImportError:
    from ContextActivity import ContextActivity

from Efficience import getEff
from Plane import PLANE_NAMES
import params as p
from pValues import pVal

class OrchestrationGraphData:
    def __init__(self, library: Library, timeBudget: int, start, goal):
        self.lib = library
        self.tBudget = timeBudget
        self.start = start
        self.reached = start
        self.goal = goal
        
        self.listOfFixedInstancedAct = []
        self.quantities = [0] * self.lib.getLength()
        self.totTime = 0

        self.hardGapsCount = 1
        self.remainingGapsDistance = start.distance_onlyForward(goal)
        self.hardGapsList = [0]

        self.gapFocus = None
        self.currentListForSelectedGap = []

    def __repr__(self):
        textList = ""
        for iAct in self.listOfFixedInstancedAct:
            textList += str(iAct) + "\n"
        return "\nThe lesson plan is:\n"\
                + textList\
                + "Time spent " + str(self.totTime) + " min (budget = "\
                + str(self.tBudget) + " min).\n"\
                + "Remains " + str(self.hardGapsCount) + " gaps to cover, "\
                + "for a \"distance\" of " + str(self.remainingGapsDistance) + ".\n"
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        activities_list = []
        for iAct in self.listOfFixedInstancedAct:
            if hasattr(iAct, 'to_dict'):
                activities_list.append(iAct.to_dict())
            else:
                activities_list.append({
                    'name': iAct.actData.name if hasattr(iAct, 'actData') else 'Unknown',
                    'time': iAct.time if hasattr(iAct, 'time') else 30,
                    'startsAfter': iAct.startsAfter if hasattr(iAct, 'startsAfter') else 0
                })
        
        return {
            'timeBudget': self.tBudget,
            'totalTime': self.totTime,
            'activities': activities_list,
            'hardGapsCount': self.hardGapsCount,
            'remainingGapsDistance': self.remainingGapsDistance,
            'hardGapsList': self.hardGapsList,
            'quantities': self.quantities
        }

    def reEvaluateData(self):
        if self.gapFocus == None:
            self.currentListForSelectedGap = self.evaluateGlobal()
        else:
            start = self.start if self.gapFocus == 0 else self.listOfFixedInstancedAct[self.gapFocus - 1].end
            end = self.goal if self.gapFocus == len(self.listOfFixedInstancedAct) else self.listOfFixedInstancedAct[self.gapFocus].start
            self.currentListForSelectedGap = self.evaluateFor(start, end)
    
    def evaluateGlobal(self):
        result = []
        for i in range(self.lib.getLength()):
            flags = self.getFlags(i)
            actData = self.lib.getActData(i)
            result.append(ContextActivity(actData, None, flags))
        return result
    
    def evaluateFor(self, start, goal):
        if p.PRINT_DETAILS_EFFICIENCE:
            print("\n\n\n==============================")
            print("PRINT_DETAILS_EFFICIENCE - from start=", start, " to goal=", goal, sep='')
        result = []
        d = start.distance_onlyForward(goal)
        
        for i in range(self.lib.getLength()):
            flags = self.getFlags(i)
            actData = self.lib.getActData(i)
            if p.PRINT_DETAILS_EFFICIENCE:
                print("\n===== Details for", actData.name)
            wouldStart, wouldEnd, _ = actData.what_from(start)
            d1 = start.distance_onlyForward(wouldStart)
            d2 = wouldEnd.distance_onlyForward(goal)
            efficiency = getEff(d, d1, d2, actData.defT, self.tBudget - self.totTime, self.remainingGapsDistance)
            if efficiency <= 0:
                flags.append("noProg")
            result.append(ContextActivity(actData, efficiency, flags))
        self.getAndSetBestFromList(result)
        return result
    
    def getAndSetBestFromList(self, listOfContextAct):
        if self.gapFocus is None:
            return None
        bestCAct = listOfContextAct[0]
        for CAct in listOfContextAct:
            if (bestCAct.okeyToTake() and not CAct.okeyToTake()):
                pass
            else:
                if ((CAct.okeyToTake() and not bestCAct.okeyToTake())
                    or (CAct.countFlags() < bestCAct.countFlags())
                    or ((bestCAct.countFlags() == CAct.countFlags())
                        and (bestCAct.myScore < CAct.myScore))):
                    bestCAct = CAct
        bestCAct.isBest = True
        return bestCAct

    def reStructurateData(self):
        current = self.start
        self.totTime = 0
        for iAct in self.listOfFixedInstancedAct:
            iAct.startsAfter = self.totTime
            self.totTime += iAct.time
            iAct.adjust(current, iAct.time)
            current = iAct.end
        self.reached = current
        self.evaluate_gaps()

    def evaluate_gaps(self):
        self.hardGapsCount = 0
        self.remainingGapsDistance = 0
        gapsToCover = []
        current = self.start
        
        for gap_idx in range(len(self.listOfFixedInstancedAct) + 1):
            if gap_idx < len(self.listOfFixedInstancedAct):
                act = self.listOfFixedInstancedAct[gap_idx]
                curr_dist = current.distance_onlyForward(act.start)
                current = act.end
            else:
                curr_dist = current.distance_onlyForward(self.goal)
                
            if p.TRESHOLD < curr_dist:
                self.hardGapsCount += 1
                self.remainingGapsDistance += curr_dist
                gapsToCover.append((curr_dist, gap_idx))

        self.hardGapsList = [item[1] for item in gapsToCover]
        return gapsToCover

    def insert(self, actIdx: int, idx: int):
        reachedBeforeIdx = self.listOfFixedInstancedAct[idx - 1].end if idx > 0 else self.start
        instanceToAdd = InstantiatedActData(self.lib.getActData(actIdx), reachedBeforeIdx)
        if len(self.listOfFixedInstancedAct) < idx:
            print("WARNING: inserted at index", idx)
        self.quantities[actIdx] += 1
        
        temp = self.listOfFixedInstancedAct
        self.listOfFixedInstancedAct = temp[:idx] + [instanceToAdd] + temp[idx:]

    def exchange(self, iActIdx: int, spaceIdx: int):
        movingInstAct = self.listOfFixedInstancedAct[iActIdx]
        modifiedListe = self.listOfFixedInstancedAct[:iActIdx] + self.listOfFixedInstancedAct[iActIdx+1:]
        if spaceIdx > iActIdx:
            spaceIdx -= 1

        preList = modifiedListe[:spaceIdx]
        postList = modifiedListe[spaceIdx:]
        self.listOfFixedInstancedAct = preList + [movingInstAct] + postList

    def remove(self, iActIdx: int):
        self.quantities[self.listOfFixedInstancedAct[iActIdx].actData.idx] -= 1
        self.listOfFixedInstancedAct = self.listOfFixedInstancedAct[:iActIdx] + self.listOfFixedInstancedAct[iActIdx+1:]

    def reset(self):
        self.quantities = [0] * self.lib.getLength()
        self.listOfFixedInstancedAct = []

    def insertBestForSelectedGap(self):
        for CAct in self.currentListForSelectedGap:
            if CAct.isBest:
                return CAct.myActData.idx

    def getFlags(self, actIdx: int):
        flags = []
        if self.lib.getActData(actIdx).maxRepetition <= self.quantities[actIdx]:
            flags.append("tooM")
        if self.tBudget < self.totTime + self.lib.getActData(actIdx).defT:
            flags.append("long")
        return flags

    def saveAsFile(self, filename: str):
        if not filename.endswith(".pickle"):
            filename += ".pickle"
        with open(filename, 'wb') as f:
            pickle.dump(self, f, pickle.HIGHEST_PROTOCOL)

    def loadFromFile(filename: str):
        if not filename.endswith(".pickle"):
            filename += ".pickle"
        with open(filename, 'rb') as f:
            return pickle.load(f)


class OrchestrationGraph:
    def __init__(self, library: Library = None, timeBudget: int = 120, start = None, goal = None):
        if library is None:
            # Create default library if none provided
            library = Library()
        if start is None:
            start = pVal((0.0, 0.0))
        if goal is None:
            goal = pVal((0.9, 0.9))
            
        self.data = OrchestrationGraphData(library, timeBudget, start, goal)

    def __repr__(self):
        return self.data.__repr__()
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return self.data.to_dict()
    
    def add_activity(self, activity):
        """Add an activity to the orchestration graph"""
        # This is a simplified version for API usage
        if hasattr(activity, 'to_dict'):
            self.data.listOfFixedInstancedAct.append(activity)
        else:
            # Convert simple dict to InstantiatedActData if needed
            pass
    
    def reEvaluate(self):
        self.data.reEvaluateData()

    def reStructurate(self):
        self.setGapFocus(-1)
        self.data.reStructurateData()
        self.reEvaluate()

    def setGapFocus(self, gapIdx: int):
        if gapIdx < 0:
            self.data.gapFocus = None
            self.reEvaluate()
        else:
            self.data.gapFocus = gapIdx
            self.reEvaluate()

    def insert(self, actIdx: int, idx: int):
        self.data.insert(actIdx, idx)
        self.reStructurate()

    def exchange(self, iActIdx: int, spaceIdx: int):
        self.data.exchange(iActIdx, spaceIdx)
        self.reStructurate()

    def remove(self, iActIdx: int):
        self.data.remove(iActIdx)
        self.reStructurate()

    def reset(self):
        self.data.reset()
        self.reStructurate()

    def autoAdd(self):
        temp = self.data.evaluate_gaps()
        temp.sort(reverse=True)
        self.setGapFocus(temp[0][1])
        self.autoAddFromSelectedGap()

    def autoAddFromSelectedGap(self):
        self.insert(self.data.insertBestForSelectedGap(), self.data.gapFocus)

    # Properties as regular methods/attributes
    @property
    def listeReal(self):
        return self.data.listOfFixedInstancedAct

    @property
    def listActivityForGap(self):
        return self.data.currentListForSelectedGap

    @property
    def totalTime(self):
        return self.data.totTime

    @property
    def lessonTime(self):
        return self.data.tBudget

    @property
    def hardGapList(self):
        return self.data.hardGapsList

    @property
    def remainingGapsCount(self):
        return self.data.hardGapsCount

    @property
    def isSelectedGapHard(self):
        if self.data.gapFocus is None:
            return False
        return self.data.gapFocus in self.data.hardGapsList

    @property
    def numberPlanes(self):
        return len(PLANE_NAMES)

    @property
    def labelPlanes(self):
        return PLANE_NAMES


def tests():
    myLib = Library("inputData/interpolation_2D_library.csv")
    
    print("\n===== Testing insertion and reStructuration of OrchestrationGraph. =====")
    print("We insert ALL activities from the library in their order.")
    OG1 = OrchestrationGraph(myLib, 50, pVal((0.0, 0.0)), pVal((0.9, 0.9)))
    for i in range(len(myLib.liste)):
        OG1.insert(i, i)

    print(OG1)
    print("The tests are completed.")

if __name__ == "__main__":
    tests()