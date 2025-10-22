# -*- coding: utf-8 -*-
"""
Created on Tue Feb 25 09:43:43 2025

@author: Samuel
"""

import sys
import os
import subprocess
import threading

import pickle


from Library import Library
from InstantiatedAct import InstantiatedActData
try:
    from ContextActivity_cleaned import ContextActivity
except ImportError:
    from ContextActivity import ContextActivity
from Efficience import getEff
from Plane import PLANE_NAMES

import params as p

from PyQt6.QtCore import QObject, pyqtProperty, pyqtSignal, pyqtSlot, QVariant
from PyQt6.QtCore import QUrl


#For tests
from pValues import pVal
import random as r

class OrchestrationGraphData:
    def __init__(self, library:Library, timeBudget:int, start, goal):
        self.lib = library
        self.tBudget = timeBudget
        self.start = start
        self.reached = start
        self.goal = goal
        
        self.listOfFixedInstancedAct = []
        self.quantities = [0]*self.lib.getLength()
        self.totTime = 0

        self.hardGapsCount = 1
        self.remainingGapsDistance = start.distance_onlyForward(goal)
        self.hardGapsList = [0]

        self.gapFocus = None # Index of the gap currently selected in QML.
        self.currentListForSelectedGap = [] # REQUIRED --> Segmentation Fault
        # otherwise the QML objects references to a temporary variable

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
    
    def __getstate__(self):
        # https://stackoverflow.com/questions/1939058/simple-example-of-use-of-setstate-and-getstate
        out = self.__dict__.copy()
        out.pop("currentListForSelectedGap", None)
        out.pop("gapFocus", None)
        return out
    
    def __setstate__(self, d):
        self.__dict__ = d
        self.currentListForSelectedGap = []
        self.gapFocus = None


    # ========== ACTIONNABLES ========== #

    def saveAsFile(self, filename:str):
        if not filename.endswith(".pickle"):
            filename += ".pickle"
        with open(filename, 'wb') as f:
            # Pickle the 'data' dictionary using the highest protocol available.
            pickle.dump(self, f, pickle.HIGHEST_PROTOCOL)

    def saveAsFileFromQt(self, filename:str):
        # chatGPT indicated the existance of QUrl. Find more at:
        # https://doc.qt.io/archives/qtforpython-5/PySide2/QtCore/QUrl.html

        qurl = QUrl(filename)
        if qurl.isValid():
            filename = qurl.toLocalFile()
        else:
            raise OSError("ERROR: QUrl is not valid:", filename)

        self.saveAsFile(filename)

    def saveAsTempFile(self):
        # Get the directory where the current file is located #chatGPT helped for that
        script_dir = os.path.dirname(os.path.abspath(__file__))
        save_for_print_name = os.path.join(script_dir, "temp", "saveForPrint.pickle")

        self.saveAsFile(save_for_print_name)

    def loadFromFile(filename:str):
        qurl = QUrl(filename)
        if qurl.isValid():
            filename = qurl.toLocalFile()
        else:
            print("WARNING: QUrl is not valid, using filename as is.")

        if not filename.endswith(".pickle"):
            filename += ".pickle"
        with open(filename, 'rb') as f:
            newOG = pickle.load(f)
            return newOG


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
            print("PRINT_DETAILS_EFFICIENCE - from start=", start, " to goal=", goal, sep = '')
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
            if efficiency <= 0: # For the two first efficience metrics, non-positive values indicates that the activitiy is "useless".
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
                # In this situation we should avoid taking the CAct activity and keep the current best one.
                pass
            else:
                if ((CAct.okeyToTake() and not bestCAct.okeyToTake())
                    or (CAct.countFlags() < bestCAct.countFlags()) # Then we consider the CAct activity better
                    or ((bestCAct.countFlags()  == CAct.countFlags())
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
        # returns the (distance, idx) of the all gaps to cover.
        # As well, it updates the hardGapsCount and remainingGapsDistance attributes.
        self.hardGapsCount = 0
        self.remainingGapsDistance = 0
        gapsToCover = []
        current = self.start
        
        for gap_idx in range(len(self.listOfFixedInstancedAct)+1):
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
    

    def insert(self, actIdx:int, idx:int):
        reachedBeforeIdx = self.listOfFixedInstancedAct[idx - 1].end if idx > 0 else self.start
        instanceToAdd = InstantiatedActData(self.lib.getActData(actIdx), reachedBeforeIdx)
        if len(self.listOfFixedInstancedAct) < idx:
            print("WARNING: inserted at index", idx)
        self.quantities[actIdx] += 1
        
        temp = self.listOfFixedInstancedAct
        self.listOfFixedInstancedAct = temp[:idx]\
            + [instanceToAdd] + temp[idx:]
        

    def exchange(self, iActIdx:int, spaceIdx:int):
        #    0   1   2   3   4   5   6      # InsActIndices
        #  0   1   2   3   4   5   6   7    # SpacesIndices
        movingInstAct = self.listOfFixedInstancedAct[iActIdx]
        modifiedListe = self.listOfFixedInstancedAct[:iActIdx] + self.listOfFixedInstancedAct[iActIdx+1:]  # Remove the instAct from its current position
        if spaceIdx > iActIdx: #Find the index of the goal-space with the modified list's point of view
            spaceIdx -= 1

        preList = modifiedListe[:spaceIdx]
        postList = modifiedListe[spaceIdx:]
        self.listOfFixedInstancedAct = preList + [movingInstAct] + postList


    def remove(self, iActIdx:int):
        self.quantities[self.listOfFixedInstancedAct[iActIdx].actData.idx] -= 1
        self.listOfFixedInstancedAct = self.listOfFixedInstancedAct[:iActIdx] + self.listOfFixedInstancedAct[iActIdx+1:]  # Remove the instAct from its current position
        

    def reset(self):
        self.quantities = [0]*self.lib.getLength()
        self.listOfFixedInstancedAct = []

    def insertBestForSelectedGap(self):
        for CAct in self.currentListForSelectedGap:
            if CAct.isBest:
                return CAct.myActData.idx
        

    # ========== GETTERS ========== #
    
    def getFlags(self, actIdx:int):
        flags = []
        if self.lib.getActData(actIdx).maxRepetition <= self.quantities[actIdx]:
            flags.append("tooM")
        if self.tBudget < self.totTime + self.lib.getActData(actIdx).defT:
            flags.append("long")
        return flags

  

class OrchestrationGraph(QObject):
    ogChangeSignal = pyqtSignal()
    gapSelectionChangeSignal = pyqtSignal()

    def __init__(self, library:Library, timeBudget:int, start, goal):
        super().__init__()
        self.data = OrchestrationGraphData(library, timeBudget, start, goal)
        self.setGapFocus(-1)

    def __repr__(self):
        return self.data.__repr__()
    
    def reEvaluate(self):
        self.data.reEvaluateData()
        self.gapSelectionChangeSignal.emit()

    def reStructurate(self):
        self.setGapFocus(-1)  # Reset the gap focus to avoid issues with the current gap.
        self.data.reStructurateData()
        self.reEvaluate()
        self.ogChangeSignal.emit()


    def myCallerForPrintingSubprocess(self):
        self.data.saveAsTempFile()


        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            print('running in a PyInstaller bundle')

            # This is the way for calling the process used within the built application
            try:    # This works on Linux

                # Get the directory where the current file is located #chatGPT helped for that
                script_dir = os.path.dirname(os.path.abspath(__file__))
                otherScriptPath = os.path.join(script_dir, "..", "MyOGPrinter")
                
                subprocess.run([otherScriptPath], check=True)
            except:
                print("Something went wrong during the external (technical) print.")
                print("Consider opening a second terminal at the same location and running")
                print(">>> python3 MyOGPrinter.py")
                print("in order to see that aborted print.")

        else :
            # This is the way for calling the process that work when develloping (run with python)
            # Get the directory where the current file is located #chatGPT helped for that
            script_dir = os.path.dirname(os.path.abspath(__file__))
            otherPythonPath = os.path.join(script_dir, "MyOGPrinter.py")

            subprocess.run([sys.executable, otherPythonPath], check=True)



    # ============== SLOTS ============== #
    
    @pyqtSlot()
    def forceRestructuration(self):
        self.reStructurate()

    @pyqtSlot()
    def print(self):
        # This prints as TEXT.
        print(self)
    
    @pyqtSlot()
    def myCustomPrintFunction(self):
        # This handles the TECHNICAL printing.
        # See MyOGPrinter.py for more details.

        t_thread = threading.Thread(target=self.myCallerForPrintingSubprocess)
        t_thread.daemon = True # This will allow the main program to exit even if the threads have not.
        t_thread.start()

    @pyqtSlot(str)
    def saveAsFile(self, filename):
        self.data.saveAsFileFromQt(filename)


    @pyqtSlot(str)
    def loadFromFile(self, filename):
        self.data = OrchestrationGraphData.loadFromFile(filename)
        self.reStructurate()

    @pyqtSlot(int)
    # Should always be called before listActivityForGap is required.
    def setGapFocus(self, gapIdx:int):
        if gapIdx < 0:
            self.data.gapFocus = None
            self.reEvaluate()
        else:
            self.data.gapFocus = gapIdx
            self.reEvaluate()
        self.gapSelectionChangeSignal.emit()

    @pyqtSlot(int, int)
    def insert(self, actIdx:int, idx:int):
        self.data.insert(actIdx, idx)
        self.reStructurate()

    @pyqtSlot(int, int)
    def exchange(self, iActIdx:int, spaceIdx:int):
        self.data.exchange(iActIdx, spaceIdx)
        self.reStructurate()

    @pyqtSlot(int)
    def remove(self, iActIdx:int):
        self.data.remove(iActIdx)
        self.reStructurate()


    @pyqtSlot()
    def reset(self):
        self.data.reset()
        self.reStructurate()

    @pyqtSlot()
    def autoAdd(self):
        temp = self.data.evaluate_gaps()
        temp.sort(reverse = True)
        self.setGapFocus(temp[0][1])
        self.autoAddFromSelectedGap()

    @pyqtSlot()
    def autoAddFromSelectedGap(self):
        self.insert(self.data.insertBestForSelectedGap(), self.data.gapFocus)

    
    # ============== PROPERTIES ============== #

    @pyqtProperty(QVariant, notify=ogChangeSignal)
    def listeReal(self):
        return [iActData.getQtObject() for iActData in self.data.listOfFixedInstancedAct]


    @pyqtProperty(QVariant, notify=gapSelectionChangeSignal)
    def listActivityForGap(self):
        return self.data.currentListForSelectedGap
    
    @pyqtProperty(QVariant, notify=gapSelectionChangeSignal)
    def sortedListActivityForGap(self):
        print("WARNING - sortedListActivityForGap - not sorted")
        return self.data.currentListForSelectedGap[0:-1:-1]
    

    @pyqtProperty(int, notify=ogChangeSignal)
    def totalTime(self):
        return self.data.totTime
    
    @pyqtProperty(int, notify=ogChangeSignal)
    def lessonTime(self):
        return self.data.tBudget
    
    @pyqtProperty(QVariant, notify=ogChangeSignal)
    def hardGapList(self):
        return self.data.hardGapsList
    
    @pyqtProperty(int, notify=ogChangeSignal)
    def remainingGapsCount(self):
        return self.data.hardGapsCount
    
    @pyqtProperty(bool, notify=gapSelectionChangeSignal)
    def isSelectedGapHard(self):
        if self.data.gapFocus is None:
            return False
        return self.data.gapFocus in self.data.hardGapsList

    @pyqtProperty(int, notify=ogChangeSignal)
    def numberPlanes(self):
        return len(PLANE_NAMES)
    
    @pyqtProperty(QVariant, notify=ogChangeSignal)
    def labelPlanes(self):
        return PLANE_NAMES
    
    @pyqtProperty(bool, notify=ogChangeSignal)
    def shouldOutputScore(self):
        return p.SHOULD_OUTPUT_SCORE
    


def tests():
    myLib = Library("inputData/interpolation_2D_library.csv")
    
    print("")
    print("===== Testing insertion and reStructuration of OrchestrationGraph. =====")
    print("We insert ALL activities from the library in their order.")
    OG1 = OrchestrationGraph(myLib, 50, pVal((0.0, 0.0)), pVal((0.9, 0.9)))
    for i in range(len(myLib.liste)):
        OG1.insert(i, i)

    print(OG1)
    OG1.myCustomPrintFunction()
    input("Press Enter to continue... (after the visual representation has appeared)")

    print("We shuffle the activities in a random order whitout modifying them (this is not a feature of the class, but a test).")
    r.shuffle(OG1.data.listOfFixedInstancedAct)
    print("After shuffling, the Instantiated Activities are the same but in a different order and the technical representation (visual) has a lot of arrows to it.")
    print(OG1)
    OG1.myCustomPrintFunction()
    input("Press Enter to continue... (after the visual representation has appeared)")

    print("Now we re-structurate the graph which will modify the instantiated activities to adapt to this new order.")
    OG1.reStructurate()
    print(OG1)
    OG1.myCustomPrintFunction()
    input("Press Enter to continue... (after the visual representation has appeared)")
    
    print("")
    print("")
    print("===== Testing autoAddFromSelectedGap =====")
    print("Now we reset the graph to its original state and add the recommended activity until no hard transition remains.")
    OG1.reset()
    while 0 < OG1.remainingGapsCount:
        OG1.autoAdd()
        print(OG1)
        OG1.myCustomPrintFunction()
        input("Press Enter to continue... (after the visual representation has appeared)")

    print("The goal has been completed! There is no hard transition left.")


    print("")
    print("Addind the first activity of the library at the beginning of the lesson.")
    OG1.data.insert(0, 0)
    print("WARNING: this insertion has been done by blocking the re-structuration. See the result:")
    print(OG1)
    OG1.myCustomPrintFunction()
    input("Press Enter to continue... (after the visual representation has appeared)")

    print("")
    print("Now we restruturate:")
    OG1.reStructurate()
    print(OG1)
    OG1.myCustomPrintFunction()
    input("Press Enter to continue... (after the visual representation has appeared)")

    print("The tests are completed.")

if __name__=="__main__":
    tests()