# -*- coding: utf-8 -*-
"""
Created on Tue Mar 11 13:39:49 2025

@author: Samuel


This modules computes the score of an activity in a given gap (transition) in many different ways.

The "score" is an abstract concept and the choice to define it is not obvious.
Hence, this module provides several ways to compute it, and the user can choose the one that fits best their needs.

"""

import params as p
import math as m

def distRemoved(fromStartToGoal, fromStartToWouldStart, fromWouldEndToGoal, actTime, remTime, totalRemDistance):
    return (fromStartToGoal- fromStartToWouldStart - fromWouldEndToGoal)

def distRemoved_over_usedTime(fromStartToGoal, fromStartToWouldStart, fromWouldEndToGoal, actTime, remTime, totalRemDistance):
    return (fromStartToGoal- fromStartToWouldStart - fromWouldEndToGoal)/actTime

def leftTime_over_leftDist(fromStartToGoal, fromStartToWouldStart, fromWouldEndToGoal, actTime, remTime, totalRemDistance):
    leftDistance = totalRemDistance - distRemoved(fromStartToGoal, fromStartToWouldStart, fromWouldEndToGoal, actTime, remTime, totalRemDistance)
    if leftDistance < p.TRESHOLD:
        return m.inf
    return (remTime - actTime)/leftDistance

    

def getEff(fromStartToGoal, fromStartToWouldStart, fromWouldEndToGoal, actTime, remTime, totalRemDistance):
    distRemoved_                = distRemoved               (fromStartToGoal, fromStartToWouldStart, fromWouldEndToGoal, actTime, remTime, totalRemDistance)
    distRemoved_over_usedTime_  = distRemoved_over_usedTime (fromStartToGoal, fromStartToWouldStart, fromWouldEndToGoal, actTime, remTime, totalRemDistance)
    leftTime_over_leftDist_     = leftTime_over_leftDist    (fromStartToGoal, fromStartToWouldStart, fromWouldEndToGoal, actTime, remTime, totalRemDistance)
    if p.PRINT_DETAILS_EFFICIENCE:
        print(  "tot=",          round(fromStartToGoal, 2),       sep = '', end = ", ")
        print(  "toWouldStard=", round(fromStartToWouldStart, 2), sep = '', end = ", ")
        print(  "fromWouldEnd=", round(fromWouldEndToGoal, 2),    sep = ''           )
        print(  "time=",    round(actTime, 2), sep = '', end = ", ")
        print(  "remTime=", round(remTime, 2), sep = '',           )
        print("")
        print(  "distRem=",                 round(distRemoved_, 4),               sep = '', end = ", ")
        print(  "distRem/time=",            round(distRemoved_over_usedTime_, 4), sep = '', end = ", ")
        print(  "leftTime/leftDistance=",   round(leftTime_over_leftDist_, 2),    sep = ''           )
    
    # Here is the choice you can make. The first uncommented "return" will be used.

    # This favorises the activity which "removes" the most imcomprehension from the students.
    #return distRemoved_

    # THIS IS THE DEFAULT HEURISTIC
    # This favorises the activity which "removes" the most imcomprehension from the students with the LEAST time used.
    return distRemoved_over_usedTime_


    # This favorises the activity which leaves the most time for the least imcomprehension.
    # WARNING: Despite its elegance this have big problems.
    # return leftTime_over_leftDist_