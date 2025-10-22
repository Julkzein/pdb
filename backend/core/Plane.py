"""
    This modules converts integers representing planes to the corresponding string.
    The names are defined in params.py and should correspond with the input data.
"""

from params import PLANE_NAMES, PLANE_DESCRIPTIONS

def intFromPlane(string : str):
    # Convert a string representing the plane to an int
    return PLANE_NAMES.index(string)
        
def planeFromInt(idx : int):
    # Convert a string representing the plane to an int
    if 0 <= idx < len(PLANE_NAMES):
        return PLANE_NAMES[idx]
    else:
        raise ValueError('Error - planeFromInt: invalid idx.')
    
def descriptionFromInt(idx : int):
    # Convert a string representing the plane to an int
    if 0 <= idx < len(PLANE_NAMES):
        return PLANE_DESCRIPTIONS[idx]
    else:
        raise ValueError('Error - descriptionFromInt: invalid idx.')