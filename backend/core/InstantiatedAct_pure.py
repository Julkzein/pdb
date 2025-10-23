# -*- coding: utf-8 -*-
"""
Pure Python implementation of InstantiatedAct (no Qt dependencies)
Represents a specific instance of an activity in the lesson timeline
"""

from pValues_pure import pVal


class InstantiatedActData:
    """
    An instantiated activity - a specific occurrence of an activity template
    in the lesson timeline with chosen time, plane, and state progression.
    """

    def __init__(self, actData, time, plane, startsAfter, pValStart):
        """
        Args:
            actData: ActivityData reference
            time: chosen duration for this instance
            plane: chosen plane (0=Indiv, 1=Team, 2=Class)
            startsAfter: cumulative time before this activity starts
            pValStart: pValue state at start of this activity
        """
        self.actData = actData
        self.time = time
        self.plane = plane
        self.startsAfter = startsAfter

        # Calculate state progression
        self.pValStart = pValStart

        # Ensure prerequisites are met
        if not pValStart.isPast(actData.pcond):
            # Need to advance to meet prerequisites
            self.pValStart = pValStart.needToReach(actData.pcond)

        # Calculate end state
        effect = actData.peffect.get(time)
        self.pValEnd = self.pValStart.plus(effect)

    def adjust(self, newStartsAfter, newPValStart):
        """
        Adjust this activity's position in timeline.
        Used when activities are inserted/removed before this one.

        Args:
            newStartsAfter: new cumulative start time
            newPValStart: new starting pValue
        """
        self.startsAfter = newStartsAfter

        # Recalculate state progression
        self.pValStart = newPValStart.needToReach(self.actData.pcond)
        effect = self.actData.peffect.get(self.time)
        self.pValEnd = self.pValStart.plus(effect)

    def endsAfter(self):
        """Get cumulative time when this activity ends"""
        return self.startsAfter + self.time

    def toString(self, detailed=False):
        """Human-readable string representation"""
        plane_names = ["Indiv.", "Team", "Class"]
        plane_str = plane_names[self.plane] if 0 <= self.plane < 3 else f"Plane{self.plane}"

        string = f"{self.actData.name:>20} [{plane_str:>6}] {self.time:>3}'"

        if detailed:
            string += f" | starts@{self.startsAfter}' | {self.pValStart} -> {self.pValEnd}"

        return string

    def __repr__(self):
        return self.toString(False)

    def __str__(self):
        return self.toString(True)

    def to_dict(self):
        """Serialize to dictionary for JSON"""
        return {
            'activityIdx': self.actData.idx,
            'activityName': self.actData.name,
            'activityDescription': self.actData.getDescription(),
            'time': self.time,
            'plane': self.plane,
            'startsAfter': self.startsAfter,
            'endsAfter': self.endsAfter(),
            'pValStart': self.pValStart.to_dict(),
            'pValEnd': self.pValEnd.to_dict()
        }

    @classmethod
    def from_dict_with_library(cls, data, library):
        """
        Deserialize from dictionary with library reference

        Args:
            data: dictionary from to_dict()
            library: Library instance to look up ActivityData
        """
        actData = library.getActData(data['activityIdx'])
        if actData is None:
            raise ValueError(f"Activity index {data['activityIdx']} not found in library")

        pValStart = pVal.from_dict(data['pValStart'])

        return cls(
            actData=actData,
            time=data['time'],
            plane=data['plane'],
            startsAfter=data['startsAfter'],
            pValStart=pValStart
        )


# Test function
def test_instantiated_act():
    """Test instantiated activity operations"""
    from Activity_pure import ActivityData

    # Create a test activity
    line = "PracticeMemory,(0.2;0.2),(0.2;0.0),10,(0.5;0.0),30,15,2,Indiv."
    activity = ActivityData(line, 0)

    # Instantiate it
    start = pVal((0.0, 0.0))
    inst = InstantiatedActData(
        actData=activity,
        time=15,
        plane=0,
        startsAfter=0,
        pValStart=start
    )

    print(f"Instantiated activity: {inst}")
    print(f"Ends after: {inst.endsAfter()}'")
    print(f"State progression: {inst.pValStart} -> {inst.pValEnd}")

    # Test adjust
    print("\nAdjusting to start at 20' with new start state...")
    new_start = pVal((0.3, 0.1))
    inst.adjust(20, new_start)
    print(f"After adjustment: {inst}")
    print(f"Ends after: {inst.endsAfter()}'")


if __name__ == "__main__":
    print("=== Testing InstantiatedAct ===")
    test_instantiated_act()
