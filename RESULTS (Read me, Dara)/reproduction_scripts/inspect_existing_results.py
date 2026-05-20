import os
import sys
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')
base_dir = r"C:\Diploma\permafrost_analysis"

print("=== INSPECTING LENA LAG CSV ===")
lag_path = os.path.join(base_dir, "результаты", "lena_lag.csv")
if os.path.exists(lag_path):
    try:
        df = pd.read_csv(lag_path)
        print(df.to_string(index=False))
    except Exception as e:
        print("Error:", e)

print("\n=== INSPECTING WATER LEVEL PEAK LAGS YAKUTSK CSV ===")
peak_lag_path = os.path.join(base_dir, "результаты", "water_level_peak_lags_yakutsk.csv")
if os.path.exists(peak_lag_path):
    try:
        df = pd.read_csv(peak_lag_path)
        print(df.to_string(index=False))
    except Exception as e:
        print("Error:", e)

print("\n=== INSPECTING ANOMALY CHS LINKED CSV ===")
anomaly_chs_path = os.path.join(base_dir, "результаты", "anomaly_chs_linked.csv")
if os.path.exists(anomaly_chs_path):
    try:
        df = pd.read_csv(anomaly_chs_path)
        print(df.to_string(index=False))
    except Exception as e:
        print("Error:", e)

print("\n=== INSPECTING WATER LEVEL MONTHLY CORR CSV ===")
corr_path = os.path.join(base_dir, "результаты", "water_level_monthly_corr.csv")
if os.path.exists(corr_path):
    try:
        df = pd.read_csv(corr_path)
        print(df.to_string(index=False))
    except Exception as e:
        print("Error:", e)

print("\n=== INSPECTING МЕСЯЦЕВ.TXT ===")
mes_path = os.path.join(base_dir, "детекция дней", "месяцев.txt")
if os.path.exists(mes_path):
    try:
        with open(mes_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = [f.readline().strip() for _ in range(15)]
        print("First 15 lines of месяцев.txt:")
        for l in lines:
            print("  ", l)
    except Exception as e:
        print("Error:", e)
