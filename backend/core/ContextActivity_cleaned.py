# -*- coding: utf-8 -*-
"""
ContextActivity without PyQt6 dependencies
Modified for web backend usage
"""

from Activity_cleaned import ActivityData

class FlagContainer:
    def __init__(self, flag_list):
        self.exhausted = "tooM" in flag_list
        self.tooLong = "long" in flag_list
        self.noProgress = "noProg" in flag_list
    
    def countFlags(self):
        som = 0
        if self.exhausted:
            som += 1
        if self.tooLong:
            som += 1
        return som
    
    def to_dict(self):
        return {
            'exhausted': self.exhausted,
            'tooLong': self.tooLong,
            'noProgress': self.noProgress
        }
    
    def __repr__(self):
        return f"FlagContainer(exhausted={self.exhausted}, tooLong={self.tooLong}, makesNoProgress={self.noProgress})"

class ContextActivity:
    def __init__(self, activity: ActivityData, score: float, flags):
        self.myActData = activity
        self.myScore = score
        self.myFlags = FlagContainer(flags)
        self.isBest = False  # by default

    def __repr__(self):
        return f"ContextActivity({self.myActData.name}, {self.myScore}, {self.myFlags})"

    def countFlags(self):
        return self.myFlags.countFlags()
    
    def okeyToTake(self):
        return not self.myFlags.noProgress
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'activity': self.myActData.to_dict(),
            'score': self.myScore,
            'flags': self.myFlags.to_dict(),
            'isRecommended': self.isBest,
            'hasScore': self.myScore is not None
        }

def tests():
    print("No tests for ContextActivity")
    
if __name__ == "__main__":
    tests()