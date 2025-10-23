# -*- coding: utf-8 -*-
"""
Pure Python implementation of Efficience (no Qt dependencies)
Scoring heuristics for evaluating activity effectiveness in filling gaps
"""

# Configuration
PRINT_DETAILS = False  # Set to True for debugging
THRESHOLD = 0.05


def distRemoved(fromStartToGoal, fromStartToWouldStart, fromWouldEndToGoal, actTime, remTime, totalRemDistance):
    """
    How much distance (toward goal) would be removed by this activity.
    Simple measure of progress.
    """
    return fromStartToGoal - fromStartToWouldStart - fromWouldEndToGoal


def distRemoved_over_usedTime(fromStartToGoal, fromStartToWouldStart, fromWouldEndToGoal, actTime, remTime,
                               totalRemDistance):
    """
    Distance removed per minute spent.
    This is the PRIMARY heuristic used.
    """
    dist = distRemoved(fromStartToGoal, fromStartToWouldStart, fromWouldEndToGoal, actTime, remTime, totalRemDistance)
    if actTime == 0:
        return 0
    return dist / actTime


def leftTime_over_leftDist(fromStartToGoal, fromStartToWouldStart, fromWouldEndToGoal, actTime, remTime,
                            totalRemDistance):
    """
    Ratio of remaining time to remaining distance after this activity.
    Higher is better (more time available per unit distance).
    Returns infinity if distance becomes negligible.
    """
    dist = distRemoved(fromStartToGoal, fromStartToWouldStart, fromWouldEndToGoal, actTime, remTime, totalRemDistance)
    leftDistance = totalRemDistance - dist

    if leftDistance < THRESHOLD:
        return float('inf')

    timeLeft = remTime - actTime
    if timeLeft <= 0:
        return 0

    return timeLeft / leftDistance


def getEff(fromStartToGoal, fromStartToWouldStart, fromWouldEndToGoal, actTime, remTime, totalRemDistance):
    """
    Calculate efficiency score for an activity in a specific gap.

    Args:
        fromStartToGoal: distance from current state to goal
        fromStartToWouldStart: distance from current to where activity starts (after prereqs)
        fromWouldEndToGoal: distance from where activity ends to goal
        actTime: activity duration
        remTime: remaining time budget
        totalRemDistance: total remaining distance across all gaps

    Returns:
        float: efficiency score (higher is better)
    """
    distRemoved_ = distRemoved(fromStartToGoal, fromStartToWouldStart, fromWouldEndToGoal, actTime, remTime,
                               totalRemDistance)
    distRemoved_over_usedTime_ = distRemoved_over_usedTime(fromStartToGoal, fromStartToWouldStart, fromWouldEndToGoal,
                                                            actTime, remTime, totalRemDistance)
    leftTime_over_leftDist_ = leftTime_over_leftDist(fromStartToGoal, fromStartToWouldStart, fromWouldEndToGoal,
                                                      actTime, remTime, totalRemDistance)

    if PRINT_DETAILS:
        print(f"tot={fromStartToGoal:.2f}, toWouldStart={fromStartToWouldStart:.2f}, "
              f"fromWouldEnd={fromWouldEndToGoal:.2f}")
        print(f"time={actTime:.2f}, remTime={remTime:.2f}")
        print(f"distRem={distRemoved_:.4f}, distRem/time={distRemoved_over_usedTime_:.4f}, "
              f"leftTime/leftDistance={leftTime_over_leftDist_:.2f}")

    # Return primary heuristic
    return distRemoved_over_usedTime_


# Test function
def test_efficience():
    """Test efficiency scoring"""
    print("=== Testing Efficience ===\n")

    # Scenario: Gap of 0.5 units, 60 minutes remaining, total remaining distance 1.0
    # Activity A: moves 0.3 units in 20 minutes
    # Activity B: moves 0.4 units in 35 minutes

    print("Scenario: Gap of 0.5 units to goal, 60 min remaining")
    print("-" * 50)

    # Activity A
    score_a = getEff(
        fromStartToGoal=0.5,
        fromStartToWouldStart=0.0,  # No prerequisite gap
        fromWouldEndToGoal=0.2,  # 0.5 - 0.3 = 0.2 remaining
        actTime=20,
        remTime=60,
        totalRemDistance=1.0
    )
    print(f"Activity A (0.3 progress in 20'): score = {score_a:.4f}")

    # Activity B
    score_b = getEff(
        fromStartToGoal=0.5,
        fromStartToWouldStart=0.0,
        fromWouldEndToGoal=0.1,  # 0.5 - 0.4 = 0.1 remaining
        actTime=35,
        remTime=60,
        totalRemDistance=1.0
    )
    print(f"Activity B (0.4 progress in 35'): score = {score_b:.4f}")

    print(f"\n{'Activity A' if score_a > score_b else 'Activity B'} is more efficient!")

    # Test with prerequisite gap
    print("\n" + "=" * 50)
    print("Scenario: Activity needs prerequisite work (0.1 gap)")
    print("-" * 50)

    score_c = getEff(
        fromStartToGoal=0.5,
        fromStartToWouldStart=0.1,  # Need to cover 0.1 first
        fromWouldEndToGoal=0.2,
        actTime=20,
        remTime=60,
        totalRemDistance=1.0
    )
    print(f"Activity with prereq gap: score = {score_c:.4f}")
    print("(Score is lower because prerequisite work reduces net progress)")


if __name__ == "__main__":
    test_efficience()
