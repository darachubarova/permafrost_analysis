#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Automated unit testing and verification suite for the permafrost_model package.
Asserts mathematical correctness of calibrated regressions, travel lags, and DSS thresholding.
"""

import sys
import os
import unittest
import pandas as pd
import numpy as np

# Adjust paths to import permafrost_model
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from permafrost_model import (
    StefanClassicModel,
    StefanHybridModel,
    EmpiricalRegressionModel,
    SoilThermalTrendModel,
    HydroPropagationModel,
    DecisionSupportSystem,
    PSRS_Scorer
)

class TestStefanModels(unittest.TestCase):
    """
    Unit tests for Active Layer Thickness (ALT) solvers
    """
    def setUp(self):
        self.classic = StefanClassicModel(E=4.3448)
        self.hybrid = StefanHybridModel(E_base=4.1866, beta=0.00155)
        self.empirical = EmpiricalRegressionModel(c0=197.99, c1=0.0096, c2=-0.0051, c3=0.370, c4=-0.0045)

    def test_stefan_classic(self):
        # Known value: DDT = 2000
        # ALT = 4.3448 * sqrt(2000)
        expected = 4.3448 * np.sqrt(2000)
        pred = self.classic.predict(2000)
        self.assertAlmostEqual(pred, expected, places=4)
        
        # Negative DDT should return 0.0
        self.assertEqual(self.classic.predict(-100), 0.0)

    def test_stefan_hybrid(self):
        # Known value: DDT = 2000, H_snow = 40 cm
        # ALT = 4.1866 * sqrt(2000) * (1 + 0.00155 * 40)
        expected = 4.1866 * np.sqrt(2000) * (1.0 + 0.00155 * 40.0)
        pred = self.hybrid.predict(2000, 40.0)
        self.assertAlmostEqual(pred, expected, places=4)
        
        # Negative DDT should return 0.0
        self.assertEqual(self.hybrid.predict(-50, 20.0), 0.0)

    def test_empirical_regression(self):
        # Known values: DDT = 2000, DDF = 4000, H_snow = 40, P_summer = 150
        # ALT = 197.99 + 0.0096 * DDT - 0.0051 * DDF + 0.370 * H_snow - 0.0045 * P_summer
        expected = 197.99 + 0.0096 * 2000 - 0.0051 * 4000 + 0.370 * 40.0 - 0.0045 * 150.0
        pred = self.empirical.predict(2000, 4000, 40.0, 150.0)
        self.assertAlmostEqual(pred, expected, places=4)


class TestThermalTrendModel(unittest.TestCase):
    """
    Unit tests for deep soil warming linear projection models
    """
    def setUp(self):
        self.model = SoilThermalTrendModel(slope=0.02150, intercept=-43.44)

    def test_prediction(self):
        # T_320 = 0.0215 * 2024 - 43.44 = 0.076
        pred = self.model.predict(2024)
        self.assertAlmostEqual(pred, 0.076, places=5)

    def test_failure_year(self):
        # failure_year = -(-43.44) / 0.02150 = 2020.46511...
        fail_yr = self.model.get_failure_year()
        self.assertAlmostEqual(fail_yr, 2020.465116, places=5)
        
        # Flat warming slope should indicate infinite failure year
        flat_model = SoilThermalTrendModel(slope=0.0, intercept=-0.5)
        self.assertEqual(flat_model.get_failure_year(), float('inf'))

    def test_dynamic_fit(self):
        # Generate clean synthetic data: y = 0.05 * x - 100
        years = np.array([2000, 2010, 2020, 2030])
        temps = 0.05 * years - 100.0
        
        slope, intercept = self.model.fit(years, temps)
        self.assertAlmostEqual(slope, 0.05, places=5)
        self.assertAlmostEqual(intercept, -100.0, places=5)
        
        # Verify dynamic predictions match the new fit
        self.assertAlmostEqual(self.model.predict(2040), 2.0, places=5)


class TestHydroPropagationModel(unittest.TestCase):
    """
    Unit tests for river wave propagation travel times and warning thresholds
    """
    def setUp(self):
        self.model = HydroPropagationModel()

    def test_peak_level_prediction(self):
        # H_ykt = -120.0 + 0.38 * H_lensk + 0.42 * H_olek
        # If lensk = 600, olek = 800
        # Expected: -120.0 + 0.38*600 + 0.42*800 = -120 + 228 + 336 = 444.0
        pred = self.model.predict_peak_level(600.0, 800.0)
        self.assertAlmostEqual(pred, 444.0, places=4)

    def test_peak_date_prediction(self):
        base_date = pd.Timestamp("2026-05-10")
        
        # Lensk to Yakutsk travel lag: 4.4 days -> rounded to 4 days in code
        pred_date = self.model.predict_peak_date(base_date, origin='lensk')
        expected_date = base_date + pd.Timedelta(days=4)
        self.assertEqual(pred_date, expected_date)

        # Olekminsk to Yakutsk lag: 3.9 days -> rounded to 4 days
        pred_olek = self.model.predict_peak_date(base_date, origin='olekminsk')
        expected_olek = base_date + pd.Timedelta(days=4)
        self.assertEqual(pred_olek, expected_olek)
        
        # Yakutsk to Zhigansk: 3.8 days -> rounded to 4 days
        pred_zhig = self.model.predict_downstream_date(base_date)
        expected_zhig = base_date + pd.Timedelta(days=4)
        self.assertEqual(pred_zhig, expected_zhig)

    def test_warning_logic(self):
        # Normal
        status, msg = self.model.evaluate_warning(500)
        self.assertEqual(status, "NORMAL")
        
        # Warning (700 cm)
        status, msg = self.model.evaluate_warning(750)
        self.assertEqual(status, "WARNING")
        
        # Critical (850 cm)
        status, msg = self.model.evaluate_warning(900)
        self.assertEqual(status, "CRITICAL")


class TestDSSScorer(unittest.TestCase):
    """
    Unit tests for Permafrost Settlement Risk Score (PSRS) and EMERCOM Action Zones
    """
    def setUp(self):
        self.scorer = PSRS_Scorer()
        self.dss = DecisionSupportSystem()

    def test_z_score_calculation(self):
        # Baseline alt: mean = 221.5, std = 12.8
        # For alt = 234.3 (Z = +1.0)
        z = self.scorer.compute_z(234.3, 'alt')
        self.assertAlmostEqual(z, 1.0, places=4)

    def test_psrs_calculation(self):
        # Set all values exactly at their mean (Z = 0)
        # PSRS = 5.0 + 1.6 * (0.0) = 5.0
        score = self.scorer.calculate_score(221.5, -0.58, 35.4, 1.6)
        self.assertAlmostEqual(score, 5.0, places=4)
        
        # Extreme negative anomaly should clip at 0.0
        score_low = self.scorer.calculate_score(150.0, -2.0, 10.0, 0.0)
        self.assertEqual(score_low, 0.0)
        
        # Extreme positive anomaly should clip at 10.0
        score_high = self.scorer.calculate_score(300.0, 1.0, 80.0, 10.0)
        self.assertEqual(score_high, 10.0)

    def test_dss_severity_guidelines(self):
        # Case 1: Low risk (PSRS < 4.0)
        eval_low = self.dss.evaluate_year(200.0, -1.0, 20.0, 0.0)
        self.assertEqual(eval_low['level'], "LOW")
        self.assertEqual(eval_low['color'], "GREEN")
        self.assertTrue(len(eval_low['recommendations_ru']) >= 3)
        self.assertTrue(len(eval_low['recommendations_en']) >= 3)
        
        # Case 2: Moderate risk (4.0 <= PSRS < 7.0)
        # At means PSRS = 5.0
        eval_mod = self.dss.evaluate_year(221.5, -0.58, 35.4, 1.6)
        self.assertEqual(eval_mod['level'], "MODERATE")
        self.assertEqual(eval_mod['color'], "YELLOW")
        
        # Case 3: Extreme risk (PSRS >= 7.0)
        eval_ext = self.dss.evaluate_year(260.0, 0.2, 60.0, 5.0)
        self.assertEqual(eval_ext['level'], "EXTREME")
        self.assertEqual(eval_ext['color'], "RED")
        self.assertTrue(any("ЧС" in r for r in eval_ext['recommendations_ru']))


if __name__ == '__main__':
    print("=== STARTING AUTOMATED PERMAFROST_MODEL TESTS ===")
    unittest.main()
