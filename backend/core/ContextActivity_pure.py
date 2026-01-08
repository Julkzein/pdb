"""
Pure Python implementation of ContextActivity (no Qt dependencies)
Represents an activity with evaluation metadata for gap recommendations
"""


class FlagContainer:
    """
    Flags indicating issues with an activity choice for a specific gap
    """

    def __init__(self, flag_list):
        """
        Args:
            flag_list: list of string flags like ["tooM", "long", "noProg"]
        """
        self.exhausted = "tooM" in flag_list  # Activity used too many times
        self.tooLong = "long" in flag_list  # Activity too long for remaining time
        self.noProgress = "noProg" in flag_list  # Activity makes no progress toward goal

    def countFlags(self):
        """Count active flags (excludes noProgress)"""
        count = 0
        if self.exhausted:
            count += 1
        if self.tooLong:
            count += 1
        return count

    def to_dict(self):
        """Serialize to dictionary"""
        return {
            'exhausted': self.exhausted,
            'tooLong': self.tooLong,
            'noProgress': self.noProgress
        }


class ContextActivity:
    """
    An activity with evaluation context for a specific gap.
    Used to show scored/flagged recommendations in the UI.
    """

    def __init__(self, actData, score=None, flags=None, isBest=False):
        """
        Args:
            actData: ActivityData instance
            score: efficiency score (float), higher is better
            flags: FlagContainer or list of flag strings
            isBest: whether this is the best recommendation
        """
        self.myActData = actData
        self.myScore = score
        self.isBest = isBest

        # Handle flags
        if flags is None:
            self.myFlags = FlagContainer([])
        elif isinstance(flags, FlagContainer):
            self.myFlags = flags
        elif isinstance(flags, list):
            self.myFlags = FlagContainer(flags)
        else:
            self.myFlags = FlagContainer([])

    def countFlags(self):
        """Count active flags"""
        return self.myFlags.countFlags()

    def okeyToTake(self):
        """Returns True if activity is valid (makes progress and not exhausted/too long)"""
        return not self.myFlags.noProgress and not self.myFlags.exhausted and not self.myFlags.tooLong

    def makesNoProgress(self):
        """Returns True if activity doesn't advance toward goal"""
        return self.myFlags.noProgress

    def toString(self):
        """Human-readable string representation"""
        flags_str = []
        if self.myFlags.exhausted:
            flags_str.append("EXHAUSTED")
        if self.myFlags.tooLong:
            flags_str.append("TOO_LONG")
        if self.myFlags.noProgress:
            flags_str.append("NO_PROGRESS")

        flag_part = f" [{', '.join(flags_str)}]" if flags_str else ""
        best_marker = " " if self.isBest else ""
        score_part = f" (score: {self.myScore:.4f})" if self.myScore is not None else ""

        return f"{self.myActData.name}{best_marker}{score_part}{flag_part}"

    def __repr__(self):
        return self.toString()

    def to_dict(self):
        """Serialize to dictionary for JSON"""
        return {
            'activity': self.myActData.to_dict(),
            'score': self.myScore,
            'isBest': self.isBest,
            'flags': self.myFlags.to_dict(),
            'okeyToTake': self.okeyToTake()
        }


# Test function
def test_context_activity():
    """Test context activity with flags"""
    from Activity_pure import ActivityData

    # Create a test activity
    line = "PracticeMemory,(0.2;0.2),(0.2;0.0),10,(0.5;0.0),30,15,2,Indiv."
    activity = ActivityData(line, 0)

    # Test with no flags
    ctx1 = ContextActivity(activity, score=0.85, isBest=True)
    print(f"Best activity: {ctx1}")

    # Test with flags
    ctx2 = ContextActivity(activity, score=0.45, flags=["tooM", "long"])
    print(f"Problematic activity: {ctx2}")
    print(f"  Flag count: {ctx2.countFlags()}")
    print(f"  Okay to take: {ctx2.okeyToTake()}")

    # Test with no progress flag
    ctx3 = ContextActivity(activity, score=None, flags=["noProg"])
    print(f"Invalid activity: {ctx3}")
    print(f"  Okay to take: {ctx3.okeyToTake()}")


if __name__ == "__main__":
    print("=== Testing ContextActivity ===")
    test_context_activity()
