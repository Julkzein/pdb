# -*- coding: utf-8 -*-
"""
Pure Python implementation of OrchestrationGraph (no Qt dependencies)
Core orchestration engine for lesson planning
"""

import pickle
from pValues_pure import pVal, THRESHOLD
from Activity_pure import Library
from InstantiatedAct_pure import InstantiatedActData
from ContextActivity_pure import ContextActivity
from Efficience_pure import getEff


class OrchestrationGraphData:
    """
    The main orchestration graph engine.
    Manages a sequence of instantiated activities with state progression.
    """

    def __init__(self, library, timeBudget, start, goal):
        """
        Args:
            library: Library instance with available activities
            timeBudget: maximum lesson duration in minutes
            start: pVal representing initial student state
            goal: pVal representing target student state
        """
        self.lib = library
        self.tBudget = timeBudget
        self.start = start
        self.reached = start  # Current state (end of last activity)
        self.goal = goal

        # List of instantiated activities in order
        self.listOfFixedInstancedAct = []

        # Track how many times each activity has been used
        self.quantities = [0] * self.lib.getLength()

        # Total time used
        self.totTime = 0

        # Gap tracking
        self.hardGapsCount = 1  # Initially: start -> goal is one gap
        self.remainingGapsDistance = start.distance_onlyForward(goal)
        self.hardGapsList = [0]  # Gap at position 0 (before first activity)

        # For gap selection (UI state)
        self.gapFocus = None
        self.currentListForSelectedGap = []

    def __repr__(self):
        """Human-readable representation"""
        textList = ""
        for i, iAct in enumerate(self.listOfFixedInstancedAct):
            textList += f"  {i}: {iAct}\n"

        return (f"\n=== Orchestration Graph ===\n"
                f"Activities ({len(self.listOfFixedInstancedAct)}):\n"
                f"{textList}"
                f"Time: {self.totTime}/{self.tBudget} min\n"
                f"Hard gaps: {self.hardGapsCount} (distance: {self.remainingGapsDistance:.3f})\n"
                f"Goal reached: {self.reached.isPast(self.goal)}\n")

    # ==================== FILE OPERATIONS ==================== #

    def saveAsFile(self, filename):
        """Save orchestration graph to pickle file"""
        if not filename.endswith(".pickle"):
            filename += ".pickle"

        with open(filename, 'wb') as f:
            pickle.dump(self, f, pickle.HIGHEST_PROTOCOL)

        print(f"Saved to {filename}")

    @classmethod
    def loadFromFile(cls, filename, library):
        """Load orchestration graph from pickle file"""
        with open(filename, 'rb') as f:
            obj = pickle.load(f)

        # Restore library reference
        obj.lib = library

        # Restore transient state
        if not hasattr(obj, 'gapFocus'):
            obj.gapFocus = None
        if not hasattr(obj, 'currentListForSelectedGap'):
            obj.currentListForSelectedGap = []

        print(f"Loaded from {filename}")
        return obj

    # ==================== STATE RECALCULATION ==================== #

    def reEvaluateData(self):
        """
        Recalculate all state progressions after changes.
        Must be called after insert/remove/exchange operations.
        """
        currentState = self.start
        cumulativeTime = 0

        for inst in self.listOfFixedInstancedAct:
            # Update start time
            inst.startsAfter = cumulativeTime

            # Update state progression
            inst.adjust(cumulativeTime, currentState)

            # Move to next
            currentState = inst.pValEnd
            cumulativeTime += inst.time

        # Update global state
        self.reached = currentState
        self.totTime = cumulativeTime

        # Recalculate gaps
        self.evaluate_gaps()

    def evaluate_gaps(self):
        """
        Find all "hard gaps" in the sequence.
        A hard gap is where the distance from one activity's end to the next's
        prerequisite exceeds the threshold.
        """
        gaps = []
        totalDistance = 0.0

        if len(self.listOfFixedInstancedAct) == 0:
            # No activities: one gap from start to goal
            distance = self.start.distance_onlyForward(self.goal)
            if distance > THRESHOLD:
                gaps.append(0)
                totalDistance = distance
        else:
            # Check gap before first activity
            firstPrecond = self.listOfFixedInstancedAct[0].actData.pcond
            distance = self.start.distance_onlyForward(firstPrecond)
            if distance > THRESHOLD:
                gaps.append(0)
                totalDistance += distance

            # Check gaps between activities
            for i in range(len(self.listOfFixedInstancedAct) - 1):
                currentEnd = self.listOfFixedInstancedAct[i].pValEnd
                nextPrecond = self.listOfFixedInstancedAct[i + 1].actData.pcond

                distance = currentEnd.distance_onlyForward(nextPrecond)
                if distance > THRESHOLD:
                    gaps.append(i + 1)
                    totalDistance += distance

            # Check gap to goal
            lastEnd = self.listOfFixedInstancedAct[-1].pValEnd
            distance = lastEnd.distance_onlyForward(self.goal)
            if distance > THRESHOLD:
                gaps.append(len(self.listOfFixedInstancedAct))
                totalDistance += distance

        self.hardGapsList = gaps
        self.hardGapsCount = len(gaps)
        self.remainingGapsDistance = totalDistance

    # ==================== GAP EVALUATION FOR RECOMMENDATIONS ==================== #

    def evaluateFor(self, actIdx, position):
        """
        Evaluate how well an activity fits at a specific position (gap).

        Args:
            actIdx: index of activity in library
            position: insertion position (0 = before first activity)

        Returns:
            ContextActivity with score and flags
        """
        actData = self.lib.getActData(actIdx)
        if actData is None:
            return None

        flags = []

        # Get current state at insertion point
        if position == 0:
            currentState = self.start
        elif position <= len(self.listOfFixedInstancedAct):
            currentState = self.listOfFixedInstancedAct[position - 1].pValEnd
        else:
            currentState = self.reached

        # Get next prerequisite (or goal if at end)
        if position < len(self.listOfFixedInstancedAct):
            nextPrecond = self.listOfFixedInstancedAct[position].actData.pcond
        else:
            nextPrecond = self.goal

        # Check if prerequisites can be met
        if not currentState.isPast(actData.pcond):
            # Activity requires advancement just to start
            # This is allowed, but tracked
            pass

        # Check if activity has been used too many times
        if self.quantities[actIdx] >= actData.maxRepetition:
            flags.append("tooM")

        # Check if activity fits in remaining time
        remainingTime = self.tBudget - self.totTime
        if actData.defT > remainingTime:
            flags.append("long")

        # Calculate state after activity
        stateAfterPrereqs = currentState.needToReach(actData.pcond)
        effect = actData.peffect.default()
        stateAfterActivity = stateAfterPrereqs.plus(effect)

        # Check if activity makes progress toward next prerequisite
        distBefore = currentState.distance_onlyForward(nextPrecond)
        distAfter = stateAfterActivity.distance_onlyForward(nextPrecond)

        if distAfter >= distBefore - 0.001:  # No meaningful progress
            flags.append("noProg")
            return ContextActivity(actData, score=None, flags=flags, isBest=False)

        # Calculate efficiency score using distance_onlyForward (matches original OG_QML)
        distToNext = currentState.distance_onlyForward(nextPrecond)
        distToStart = currentState.distance_onlyForward(stateAfterPrereqs)
        distEndToNext = stateAfterActivity.distance_onlyForward(nextPrecond)

        score = getEff(
            fromStartToGoal=distToNext,
            fromStartToWouldStart=distToStart,
            fromWouldEndToGoal=distEndToNext,
            actTime=actData.defT,
            remTime=remainingTime,
            totalRemDistance=self.remainingGapsDistance
        )

        return ContextActivity(actData, score=score, flags=flags, isBest=False)

    def setGapFocus(self, gapIndex):
        """
        Set focus on a specific gap and evaluate all activities for it.

        Args:
            gapIndex: position of the gap (-1 to clear selection)
        """
        self.gapFocus = gapIndex

        if gapIndex < 0:
            self.currentListForSelectedGap = []
            return

        # Evaluate all activities for this gap
        evaluations = []
        for actIdx in range(self.lib.getLength()):
            ctx = self.evaluateFor(actIdx, gapIndex)
            if ctx is not None:
                evaluations.append(ctx)

        # Sort by score (best first), with invalid activities last
        def sort_key(ctx):
            if not ctx.okeyToTake():
                return (-1, 0)  # Invalid activities last
            if ctx.myScore is None:
                return (0, 0)
            return (1, ctx.myScore)

        evaluations.sort(key=sort_key, reverse=True)

        # Mark best valid activity
        for ctx in evaluations:
            if ctx.okeyToTake() and ctx.myScore is not None:
                ctx.isBest = True
                break

        self.currentListForSelectedGap = evaluations

    # ==================== MODIFICATION OPERATIONS ==================== #

    def insert(self, actIdx, position, plane=None, time=None):
        """
        Insert an activity at a specific position.

        Args:
            actIdx: index of activity in library
            position: where to insert (0 = before first)
            plane: which plane to use (None = use default)
            time: duration (None = use default)

        Returns:
            bool: True if successful
        """
        actData = self.lib.getActData(actIdx)
        if actData is None:
            print(f"ERROR: Invalid activity index {actIdx}")
            return False

        # Use defaults if not specified
        if plane is None:
            plane = actData.defPlane
        if time is None:
            time = actData.defT

        # Get state at insertion point
        if position == 0:
            currentState = self.start
            startsAfter = 0
        elif position <= len(self.listOfFixedInstancedAct):
            prevAct = self.listOfFixedInstancedAct[position - 1]
            currentState = prevAct.pValEnd
            startsAfter = prevAct.endsAfter()
        else:
            # Insert at end
            position = len(self.listOfFixedInstancedAct)
            if len(self.listOfFixedInstancedAct) > 0:
                lastAct = self.listOfFixedInstancedAct[-1]
                currentState = lastAct.pValEnd
                startsAfter = lastAct.endsAfter()
            else:
                currentState = self.start
                startsAfter = 0

        # Create instantiated activity
        inst = InstantiatedActData(actData, time, plane, startsAfter, currentState)

        # Insert into list
        self.listOfFixedInstancedAct.insert(position, inst)

        # Update quantity tracking
        self.quantities[actIdx] += 1

        # Recalculate all states
        self.reEvaluateData()

        print(f"Inserted {actData.name} at position {position} (plane={plane}, time={time})")
        print(f"  Current timeline ({len(self.listOfFixedInstancedAct)} activities):")
        for i, act in enumerate(self.listOfFixedInstancedAct):
            print(f"      [{i}] {act.actData.name} (plane={act.plane}): {act.startsAfter}-{act.endsAfter()} ({act.time}min)")
        return True

    def remove(self, position):
        """
        Remove activity at position.

        Args:
            position: index of activity to remove

        Returns:
            bool: True if successful
        """
        if position < 0 or position >= len(self.listOfFixedInstancedAct):
            print(f"ERROR: Invalid position {position}")
            return False

        inst = self.listOfFixedInstancedAct[position]
        actIdx = inst.actData.idx

        # Remove from list
        self.listOfFixedInstancedAct.pop(position)

        # Update quantity tracking
        self.quantities[actIdx] -= 1

        # Recalculate all states
        self.reEvaluateData()

        print(f"Removed {inst.actData.name} from position {position}")
        return True

    def exchange(self, posA, posB):
        """
        Swap two activities.

        Args:
            posA, posB: positions to swap

        Returns:
            bool: True if successful
        """
        if posA < 0 or posA >= len(self.listOfFixedInstancedAct):
            print(f"ERROR: Invalid position A: {posA}")
            return False
        if posB < 0 or posB >= len(self.listOfFixedInstancedAct):
            print(f"ERROR: Invalid position B: {posB}")
            return False

        # Swap
        self.listOfFixedInstancedAct[posA], self.listOfFixedInstancedAct[posB] = \
            self.listOfFixedInstancedAct[posB], self.listOfFixedInstancedAct[posA]

        # Recalculate all states
        self.reEvaluateData()

        print(f"Exchanged positions {posA} and {posB}")
        return True

    def reset(self):
        """Clear all activities"""
        self.listOfFixedInstancedAct = []
        self.quantities = [0] * self.lib.getLength()
        self.totTime = 0
        self.reached = self.start
        self.gapFocus = None
        self.currentListForSelectedGap = []

        self.evaluate_gaps()

        print("Reset orchestration graph")

    # ==================== AUTO-ADD ALGORITHM ==================== #

    def autoAdd(self):
        """
        Automatically add the best activity for the worst gap.

        Returns:
            bool: True if an activity was added
        """
        if self.hardGapsCount == 0:
            print("No gaps to fill!")
            return False

        # Find the worst gap (largest distance)
        worstGapIdx = 0
        worstGapDistance = 0.0

        for gapIdx in self.hardGapsList:
            # Calculate gap distance
            if gapIdx == 0:
                if len(self.listOfFixedInstancedAct) == 0:
                    distance = self.start.distance_onlyForward(self.goal)
                else:
                    distance = self.start.distance_onlyForward(
                        self.listOfFixedInstancedAct[0].actData.pcond)
            elif gapIdx == len(self.listOfFixedInstancedAct):
                distance = self.listOfFixedInstancedAct[-1].pValEnd.distance_onlyForward(self.goal)
            else:
                prevEnd = self.listOfFixedInstancedAct[gapIdx - 1].pValEnd
                nextPrecond = self.listOfFixedInstancedAct[gapIdx].actData.pcond
                distance = prevEnd.distance_onlyForward(nextPrecond)

            if distance > worstGapDistance:
                worstGapDistance = distance
                worstGapIdx = gapIdx

        # Evaluate activities for this gap
        self.setGapFocus(worstGapIdx)

        # Find best valid activity
        bestActivity = None
        for ctx in self.currentListForSelectedGap:
            if ctx.okeyToTake() and ctx.myScore is not None:
                bestActivity = ctx
                break

        if bestActivity is None:
            print(f"No valid activities found for gap at position {worstGapIdx}")
            return False

        # Insert it
        success = self.insert(bestActivity.myActData.idx, worstGapIdx)

        if success:
            print(f"Auto-added {bestActivity.myActData.name} at position {worstGapIdx} "
                  f"(score: {bestActivity.myScore:.4f})")

        return success

    def autoAddFromSelectedGap(self):
        """
        Add the best activity for the currently selected gap.

        Returns:
            bool: True if an activity was added
        """
        if self.gapFocus is None or self.gapFocus < 0:
            print("No gap selected!")
            return False

        # Find best valid activity from current recommendations
        bestActivity = None
        for ctx in self.currentListForSelectedGap:
            if ctx.okeyToTake() and ctx.myScore is not None:
                bestActivity = ctx
                break

        if bestActivity is None:
            print(f"No valid activities found for selected gap")
            return False

        # Insert it
        success = self.insert(bestActivity.myActData.idx, self.gapFocus)

        if success:
            print(f"Added {bestActivity.myActData.name} to selected gap at position {self.gapFocus}")

        return success

    # ==================== SERIALIZATION FOR JSON API ==================== #

    def get_gap_pvalue_info(self):
        """
        Get p-value information for each gap position.
        Returns a list of gap info dictionaries.
        """
        gap_info = []

        # Gap before first activity (position 0)
        if len(self.listOfFixedInstancedAct) == 0:
            # Only gap: from start to goal
            distance = self.start.distance_onlyForward(self.goal)
            gap_info.append({
                'position': 0,
                'fromPValue': self.start.to_dict(),
                'toPValue': self.goal.to_dict(),
                'distance': distance,
                'isHard': distance > THRESHOLD
            })
        else:
            # Gap before first activity
            firstPrecond = self.listOfFixedInstancedAct[0].actData.pcond
            distance = self.start.distance_onlyForward(firstPrecond)
            gap_info.append({
                'position': 0,
                'fromPValue': self.start.to_dict(),
                'toPValue': firstPrecond.to_dict(),
                'distance': distance,
                'isHard': distance > THRESHOLD
            })

            # Gaps between activities
            for i in range(len(self.listOfFixedInstancedAct) - 1):
                currentEnd = self.listOfFixedInstancedAct[i].pValEnd
                nextPrecond = self.listOfFixedInstancedAct[i + 1].actData.pcond
                distance = currentEnd.distance_onlyForward(nextPrecond)

                gap_info.append({
                    'position': i + 1,
                    'fromPValue': currentEnd.to_dict(),
                    'toPValue': nextPrecond.to_dict(),
                    'distance': distance,
                    'isHard': distance > THRESHOLD
                })

            # Gap to goal (after last activity)
            lastEnd = self.listOfFixedInstancedAct[-1].pValEnd
            distance = lastEnd.distance_onlyForward(self.goal)
            gap_info.append({
                'position': len(self.listOfFixedInstancedAct),
                'fromPValue': lastEnd.to_dict(),
                'toPValue': self.goal.to_dict(),
                'distance': distance,
                'isHard': distance > THRESHOLD
            })

        return gap_info

    def to_dict(self):
        """Serialize to dictionary for JSON API"""
        return {
            'activities': [inst.to_dict() for inst in self.listOfFixedInstancedAct],
            'totTime': self.totTime,
            'tBudget': self.tBudget,
            'start': self.start.to_dict(),
            'goal': self.goal.to_dict(),
            'reached': self.reached.to_dict(),
            'hardGapsCount': self.hardGapsCount,
            'hardGapsList': self.hardGapsList,
            'remainingGapsDistance': self.remainingGapsDistance,
            'goalReached': self.reached.isPast(self.goal),
            'gapPValueInfo': self.get_gap_pvalue_info()
        }


# ==================== TEST FUNCTIONS ==================== #

def test_orchestration():
    """Test orchestration graph operations"""
    import os

    print("=== Testing OrchestrationGraph ===\n")

    # Load library
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'inputData', 'interpolation_2D_library.csv')
    library = Library(csv_path)

    # Create orchestration graph
    start = pVal((0.0, 0.0))
    goal = pVal((0.9, 0.9))
    og = OrchestrationGraphData(library, timeBudget=120, start=start, goal=goal)

    print(og)

    # Test insertion
    print("\n--- Testing Insert ---")
    og.insert(actIdx=8, position=0)  # Introduction
    og.insert(actIdx=3, position=1)  # PracticeMemory
    print(og)

    # Test gap evaluation
    print("\n--- Testing Gap Evaluation ---")
    og.setGapFocus(2)  # Gap after PracticeMemory
    print(f"Gap focus: {og.gapFocus}")
    print(f"Recommendations:")
    for i, ctx in enumerate(og.currentListForSelectedGap[:5]):
        print(f"  {i + 1}. {ctx}")

    # Test auto-add
    print("\n--- Testing Auto-Add ---")
    og.autoAdd()
    print(og)

    # Test removal
    print("\n--- Testing Remove ---")
    og.remove(1)
    print(og)


if __name__ == "__main__":
    test_orchestration()
