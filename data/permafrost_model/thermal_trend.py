import numpy as np

class SoilThermalTrendModel:
    """
    Model for analyzing and projecting deep soil temperature trends:
    T = slope * Year + intercept
    Allows prediction of temperature and estimation of the geotechnical failure year (T >= 0C).
    """
    def __init__(self, slope=0.02150, intercept=-43.44):
        self.slope = slope
        self.intercept = intercept

    def fit(self, years, temps):
        """
        Dynamically fit the linear regression model to the provided data using Ordinary Least Squares (OLS).
        :param years: 1D array-like of calendar years
        :param temps: 1D array-like of temperatures
        """
        years_arr = np.asarray(years, dtype=float)
        temps_arr = np.asarray(temps, dtype=float)
        
        # Remove NaN values
        mask = ~np.isnan(years_arr) & ~np.isnan(temps_arr)
        x = years_arr[mask]
        y = temps_arr[mask]
        
        if len(x) < 2:
            raise ValueError("Insufficient data points to fit the linear model (need at least 2 non-NaN points).")
            
        A = np.column_stack([np.ones(len(x)), x])
        w, _, _, _ = np.linalg.lstsq(A, y, rcond=None)
        
        self.intercept = w[0]
        self.slope = w[1]
        return self.slope, self.intercept

    def predict(self, year):
        """
        Predict soil temperature in degrees Celsius for a given calendar year.
        :param year: calendar year (float or int)
        """
        return self.slope * year + self.intercept

    def get_failure_year(self):
        """
        Determine the calendar year when the deep soil temperature is projected to reach 0°C.
        This threshold represents the complete loss of geotechnical load-bearing capacity of pile foundations.
        """
        if self.slope <= 0:
            return float('inf')  # No failure if warming slope is negative/flat
        # Solving slope * Year + intercept = 0 => Year = -intercept / slope
        return -self.intercept / self.slope
