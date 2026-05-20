import numpy as np

class StefanClassicModel:
    """
    Classic Stefan Model for Active Layer Thickness (ALT):
    ALT = E * sqrt(DDT)
    """
    def __init__(self, E=4.3448):
        self.E = E

    def predict(self, DDT):
        """
        Predict ALT in cm.
        :param DDT: Degree-Days of Thawing (float)
        """
        if DDT < 0:
            return 0.0
        return self.E * np.sqrt(DDT)


class StefanHybridModel:
    """
    Hybrid Stefan Model with Snow insulation:
    ALT = E_base * sqrt(DDT) * (1 + beta * H_snow)
    """
    def __init__(self, E_base=4.1866, beta=0.00155):
        self.E_base = E_base
        self.beta = beta

    def predict(self, DDT, H_snow):
        """
        Predict ALT in cm.
        :param DDT: Degree-Days of Thawing (float)
        :param H_snow: Maximum snow depth in winter (float, cm)
        """
        if DDT < 0:
            return 0.0
        return self.E_base * np.sqrt(DDT) * (1.0 + self.beta * H_snow)


class EmpiricalRegressionModel:
    """
    Calibrated Multi-Feature Empirical Regression Model for Tuymada (R42):
    ALT = c0 + c1 * DDT + c2 * DDF + c3 * H_snow + c4 * P_summer
    """
    def __init__(self, c0=197.99, c1=0.0096, c2=-0.0051, c3=0.370, c4=-0.0045):
        self.c0 = c0
        self.c1 = c1
        self.c2 = c2  # DDF is absolute freezing degree days (positive value in model, negative coefficient)
        self.c3 = c3
        self.c4 = c4

    def predict(self, DDT, DDF, H_snow, P_summer):
        """
        Predict ALT in cm.
        :param DDT: Degree-Days of Thawing (float)
        :param DDF: Degree-Days of Freezing (float, absolute sum)
        :param H_snow: Maximum snow depth in winter (float, cm)
        :param P_summer: Summer precipitation sum (float, mm)
        """
        return self.c0 + self.c1 * DDT + self.c2 * DDF + self.c3 * H_snow + self.c4 * P_summer
