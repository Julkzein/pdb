"""
Pure Python implementation of pValues (no Qt dependencies)
Parametric values for tracking student understanding progression
"""

import math

# Precision constants
PRECISION = 0.01
THRESHOLD = 0.05


def linInterp(mi, ma, val):
    """
    Linear interpolation: finds lambda such that mi + lambda * (ma - mi) = val
    """
    if (ma - mi) < 0.0000001:
        if 0.0000001 < abs(mi - val):
            print("ERROR - linInterp: val != mi while ma != mi")
        return 0
    return (val - mi) / (ma - mi)


class pVal:
    """
    Parametric Value - represents multi-dimensional understanding state
    Typically 2D: (fluency, depth) both ranging from 0 to 1
    """

    def __init__(self, tupl):
        """Initialize with tuple of floats, e.g., (0.5, 0.3)"""
        self.v = tuple(tupl) if not isinstance(tupl, tuple) else tupl

    @classmethod
    def fromString(cls, string):
        """
        Parse from string format: "(0.5;0.3)"
        """
        string = string.strip()
        if string.startswith('(') and string.endswith(')'):
            string = string[1:-1]
        values = [float(val.strip()) for val in string.split(';')]
        return cls(tuple(values))

    def toString(self):
        """Returns rounded string representation"""
        rounded = tuple(round(x, 3) for x in self.v)
        return str(rounded)

    def __str__(self):
        return self.toString()

    def __repr__(self):
        return f"pVal{self.v}"

    def needToReach(self, other):
        """
        Returns the minimum pVal needed to satisfy 'other' as a prerequisite.
        Result is component-wise maximum of self and other.
        """
        maximums = [max(self.v[idx], other.v[idx]) for idx in range(len(self.v))]
        return pVal(tuple(maximums))

    def plus(self, effect):
        """Add effect to current state"""
        res = [self.v[idx] + effect.v[idx] for idx in range(len(self.v))]
        return pVal(tuple(res))

    def minus(self, effect):
        """Subtract effect from current state"""
        res = [self.v[idx] - effect.v[idx] for idx in range(len(self.v))]
        return pVal(tuple(res))

    def times(self, val):
        """Scalar multiplication"""
        res = [self.v[idx] * val for idx in range(len(self.v))]
        return pVal(tuple(res))

    def isPast(self, other):
        """
        Returns True if self >= other in all dimensions (with precision tolerance)
        I.e., current state satisfies the prerequisite 'other'
        """
        for i in range(len(self.v)):
            if self.v[i] + PRECISION < other.v[i]:
                return False
        return True

    def distance2(self, other):
        """Returns squared Euclidean distance"""
        som = 0
        for i in range(len(self.v)):
            som += (self.v[i] - other.v[i]) ** 2
        return som

    def distance(self, other):
        """Returns Euclidean distance"""
        return math.sqrt(self.distance2(other))

    def distance2_onlyForward(self, other):
        """
        Returns squared distance considering only dimensions where self < other.
        Used for gap detection - measures how much work needed to reach prerequisite.
        """
        som = 0
        for i in range(len(self.v)):
            if self.v[i] < other.v[i]:
                som += (self.v[i] - other.v[i]) ** 2
        return som

    def distance_onlyForward(self, other):
        """Returns forward-only distance"""
        return math.sqrt(self.distance2_onlyForward(other))

    def to_dict(self):
        """Serialize to dictionary"""
        return {'v': list(self.v)}

    @classmethod
    def from_dict(cls, data):
        """Deserialize from dictionary"""
        return cls(tuple(data['v']))


class InterPVal:
    """
    Interpolated Parametric Value - represents time-dependent effects
    Effect varies linearly based on activity duration
    """

    def __init__(self, minEffect, maxEffect, minT, maxT, defT):
        """
        minEffect: pVal at minimum time
        maxEffect: pVal at maximum time
        minT, maxT, defT: time bounds and default
        """
        self.minEffect = minEffect if isinstance(minEffect, pVal) else pVal(minEffect)
        self.maxEffect = maxEffect if isinstance(maxEffect, pVal) else pVal(maxEffect)
        self.minT = minT
        self.maxT = maxT
        self.defT = defT

        # Cache default effect
        self.defEffect = self.get(defT)

    @classmethod
    def fromStrings(cls, minEffectStr, maxEffectStr, minT, maxT, defT):
        """
        Parse from string representations
        """
        minEffect = pVal.fromString(minEffectStr)
        maxEffect = pVal.fromString(maxEffectStr)
        return cls(minEffect, maxEffect, minT, maxT, defT)

    def get(self, time):
        """
        Get interpolated effect at specific time
        Linear interpolation between minEffect and maxEffect
        """
        if self.maxT == self.minT:
            return self.maxEffect

        # Calculate interpolation factor
        lambda_val = linInterp(self.minT, self.maxT, time)
        lambda_val = max(0.0, min(1.0, lambda_val))  # Clamp to [0, 1]

        # Interpolate each dimension
        result = []
        for i in range(len(self.minEffect.v)):
            val = self.minEffect.v[i] + lambda_val * (self.maxEffect.v[i] - self.minEffect.v[i])
            result.append(val)

        return pVal(tuple(result))

    def default(self):
        """Returns effect at default time"""
        return self.defEffect

    def __str__(self):
        return f"InterPVal(min={self.minEffect} @ {self.minT}', max={self.maxEffect} @ {self.maxT}')"

    def to_dict(self):
        """Serialize to dictionary"""
        return {
            'minEffect': self.minEffect.to_dict(),
            'maxEffect': self.maxEffect.to_dict(),
            'minT': self.minT,
            'maxT': self.maxT,
            'defT': self.defT
        }

    @classmethod
    def from_dict(cls, data):
        """Deserialize from dictionary"""
        return cls(
            pVal.from_dict(data['minEffect']),
            pVal.from_dict(data['maxEffect']),
            data['minT'],
            data['maxT'],
            data['defT']
        )


# Test functions
def test_pVal():
    """Test pVal basic operations"""
    p1 = pVal((0.5, 0.3))
    p2 = pVal.fromString("(0.2;0.4)")

    print(f"p1: {p1}")
    print(f"p2: {p2}")
    print(f"p1.isPast(p2): {p1.isPast(p2)}")
    print(f"distance: {p1.distance(p2)}")
    print(f"p1 + p2: {p1.plus(p2)}")

    p3 = pVal((0.1, 0.5))
    print(f"\np3: {p3}")
    print(f"p3.isPast(p2): {p3.isPast(p2)}")
    print(f"distance_onlyForward: {p3.distance_onlyForward(p2)}")


def test_InterPVal():
    """Test InterPVal interpolation"""
    interp = InterPVal.fromStrings("(0.2;0.0)", "(0.5;0.0)", 10, 30, 15)

    print(f"\nInterPVal: {interp}")
    print(f"Effect at 10': {interp.get(10)}")
    print(f"Effect at 15': {interp.get(15)}")
    print(f"Effect at 30': {interp.get(30)}")
    print(f"Default effect: {interp.default()}")


if __name__ == "__main__":
    print("=== Testing pVal ===")
    test_pVal()
    print("\n=== Testing InterPVal ===")
    test_InterPVal()
