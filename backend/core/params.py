# -*- coding: utf-8 -*-
"""
Created on Thu Mar  6 14:27:39 2025

@author: Samuel

This holds the parameters used in the program. You can (and should) adujst PLANE_NAMES according to your data.
You can also adjust PRECISION and TRESHOLD to your needs. Note that they mostly affect the detailed technical view (of the state of the class)
"""

# Insert the name as they will be present in the DATA
# And in top-down order according to GUI
PLANE_NAMES = ["Indiv.", "Team", "Class"]
PLANE_DESCRIPTIONS = ["individually", "in teams", "as a class"]

PRECISION = 0.01 # to avoid saying "not reached" when 0.00001 from goal.
TRESHOLD = 0.05 # To allow a "gap" between two pValues before saying a goal is not reached.
# NOTE: this should depend of the dimensionality.
# Another way to do would be to restrict bigger difference.

# This variable defines if the details of the efficiency computation should be printed.
PRINT_DETAILS_EFFICIENCE = False

# This variable defined if the score is shown in the GUI, as a small text near the activity.
SHOULD_OUTPUT_SCORE = False



# === Formatting strings for printing === #

# left-aligning with https://stackoverflow.com/questions/14776788/how-can-i-pad-a-string-with-spaces-from-the-right-and-left
FORMAT_NAME = '{:>20}'
FORMAT_PVAL = '{:^12}'
FORMAT_TIME = '{:>2}'



def tests():
    print("testing params")
    print("no test yet implemented")
    
if __name__=="__main__":
    tests()