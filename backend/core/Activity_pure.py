# -*- coding: utf-8 -*-
"""
Pure Python implementation of Activity (no Qt dependencies)
Represents activity templates from the library
"""

from pValues_pure import pVal, InterPVal


# Activity descriptions for UI hover information
ACTIVITY_DESCRIPTIONS = {
    'TellTheClass': 'Teacher presents information directly to the entire class',
    'DesirableDifficultyProblem': 'Students work on challenging problems that enhance long-term retention',
    'PracticeMemory': 'Individual exercises focused on memorization and recall',
    'PracticeApplication': 'Students apply learned concepts to solve practical problems',
    'PracticeAnalyse': 'Team-based analysis activities to break down and understand concepts',
    'PracticeEvaluate': 'Collaborative evaluation of ideas, solutions, or arguments',
    'PracticeCreate': 'Students create original work demonstrating mastery',
    'AdvancedOrganiser': 'Brief overview to help students organize new information',
    'Introduction': 'Initial presentation introducing the lesson topic',
    'ExplainClass': 'Teacher explains concepts with class-wide discussion'
}


class ActivityData:
    """
    Activity template from the library CSV.
    Defines prerequisites (pcond), effects (peffect), time constraints, etc.
    """

    def __init__(self, line, idx):
        """
        Parse activity from CSV line
        Format: Name,p-condition,min p-effect,min time,max p-effect,max time,def time,max repetitions,def plane
        """
        data = [field.strip() for field in line.split(',')]

        self.idx = idx
        self.name = data[0]

        # Parse p-condition (prerequisite)
        self.pcond = pVal.fromString(data[1])

        # Determine if activity has flexible time
        if data[6] != '':
            # Has min/max/default time
            self.canChangeTime = True
            minEffect = data[2]
            maxEffect = data[4]
            self.minT = int(data[3])
            self.maxT = int(data[5])
            self.defT = int(data[6])
        else:
            # Fixed time (only max time given)
            self.canChangeTime = False
            minEffect = data[4]
            maxEffect = data[4]
            self.minT = int(data[5])
            self.maxT = int(data[5])
            self.defT = int(data[5])

        # Parse p-effect (interpolated over time)
        self.peffect = InterPVal.fromStrings(minEffect, maxEffect, self.minT, self.maxT, self.defT)

        # Max repetitions allowed
        self.maxRepetition = int(data[7])

        # Default plane: "Indiv." -> 0, "Team" -> 1, "Class" -> 2
        self.defPlane = self._parsePlane(data[8])

    def _parsePlane(self, planeStr):
        """Convert plane string to index"""
        planeStr = planeStr.strip()
        if planeStr == "Indiv.":
            return 0
        elif planeStr == "Team":
            return 1
        elif planeStr == "Class":
            return 2
        else:
            print(f"Warning: Unknown plane '{planeStr}', defaulting to Indiv.")
            return 0

    def planeToString(self, planeIdx):
        """Convert plane index to string"""
        planes = ["Indiv.", "Team", "Class"]
        return planes[planeIdx] if 0 <= planeIdx < 3 else "Unknown"

    def planeDescription(self, planeIdx):
        """Get plane description"""
        descriptions = ["individually", "in teams", "as a class"]
        return descriptions[planeIdx] if 0 <= planeIdx < 3 else "unknown"

    def getDescription(self):
        """Get brief description of what this activity is about"""
        return ACTIVITY_DESCRIPTIONS.get(self.name, 'No description available')

    def what_from(self, start, customTime=None):
        """
        Calculate start and end state when this activity is performed.

        Args:
            start: pVal representing state before activity
            customTime: optional custom duration (uses defT if None)

        Returns:
            (pValStart, pValEnd) tuple
        """
        time = customTime if customTime is not None else self.defT

        # Ensure prerequisites are met (move to minimum required state)
        pValStart = start.needToReach(self.pcond)

        # Apply effect
        effect = self.peffect.get(time)
        pValEnd = pValStart.plus(effect)

        return (pValStart, pValEnd)

    def toString(self, details=False):
        """Human-readable string representation"""
        string = f"Act {self.name:>20} {{"
        string += f"from {self.pcond}"
        string += f" +{self.peffect.default()}"

        if details and self.canChangeTime:
            string += f"\n time from {self.minT}' to {self.maxT}'"
        else:
            string += f" in {self.defT}'"

        string += f" and {self.maxRepetition} max rep."
        string += f" on {self.planeToString(self.defPlane)}"
        string += "}"
        return string

    def __repr__(self):
        return self.toString(False)

    def to_dict(self):
        """Serialize to dictionary for JSON"""
        return {
            'idx': self.idx,
            'name': self.name,
            'description': self.getDescription(),
            'pcond': self.pcond.to_dict(),
            'peffect': self.peffect.to_dict(),
            'minT': self.minT,
            'maxT': self.maxT,
            'defT': self.defT,
            'canChangeTime': self.canChangeTime,
            'maxRepetition': self.maxRepetition,
            'defPlane': self.defPlane
        }

    @classmethod
    def from_dict(cls, data):
        """Deserialize from dictionary"""
        # Create empty instance
        obj = cls.__new__(cls)
        obj.idx = data['idx']
        obj.name = data['name']
        obj.pcond = pVal.from_dict(data['pcond'])
        obj.peffect = InterPVal.from_dict(data['peffect'])
        obj.minT = data['minT']
        obj.maxT = data['maxT']
        obj.defT = data['defT']
        obj.canChangeTime = data['canChangeTime']
        obj.maxRepetition = data['maxRepetition']
        obj.defPlane = data['defPlane']
        return obj


class Library:
    """
    Collection of activity templates loaded from CSV
    """

    def __init__(self, filename):
        """Load activities from CSV file"""
        self.activities = []

        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Skip header
        for idx, line in enumerate(lines[1:]):
            line = line.strip()
            if line:  # Skip empty lines
                try:
                    activity = ActivityData(line, idx)
                    self.activities.append(activity)
                except Exception as e:
                    print(f"Error parsing line {idx + 1}: {e}")
                    print(f"Line content: {line}")

        print(f"Loaded {len(self.activities)} activities from {filename}")

    def getLength(self):
        """Get number of activities"""
        return len(self.activities)

    def getActData(self, idx):
        """Get activity by index"""
        if 0 <= idx < len(self.activities):
            return self.activities[idx]
        else:
            print(f"ERROR: Activity index {idx} out of range (0-{len(self.activities) - 1})")
            return None

    def listeActData(self):
        """Get all activities"""
        return self.activities

    def __str__(self):
        result = f"Library with {len(self.activities)} activities:\n"
        for act in self.activities:
            result += f"  {act}\n"
        return result

    def to_dict(self):
        """Serialize to dictionary"""
        return {
            'activities': [act.to_dict() for act in self.activities]
        }


# Test function
def test_activity():
    """Test activity parsing and operations"""
    # Create a test CSV line
    line = "PracticeMemory,(0.2;0.2),(0.2;0.0),10,(0.5;0.0),30,15,2,Indiv."

    activity = ActivityData(line, 0)

    print(f"Activity: {activity}")
    print(f"\nCan change time: {activity.canChangeTime}")
    print(f"Time range: {activity.minT}-{activity.maxT} (default: {activity.defT})")
    print(f"Max repetitions: {activity.maxRepetition}")
    print(f"Default plane: {activity.planeToString(activity.defPlane)}")

    # Test what_from
    start = pVal((0.0, 0.0))
    print(f"\nStarting from {start}:")
    pValStart, pValEnd = activity.what_from(start)
    print(f"  After prerequisites met: {pValStart}")
    print(f"  After activity: {pValEnd}")

    # Test with custom time
    print(f"\nWith 30-minute duration:")
    pValStart, pValEnd = activity.what_from(start, 30)
    print(f"  After activity: {pValEnd}")


if __name__ == "__main__":
    print("=== Testing Activity ===")
    test_activity()
