import os
import sys
import shutil

sys.stdout.reconfigure(encoding='utf-8')
base_dir = r"C:\Diploma\permafrost_analysis"
results_dir = os.path.join(base_dir, "RESULTS (Read me, Dara)")

# Create folders inside RESULTS for neat organization
data_dest = os.path.join(results_dir, "data_tables")
plots_dest = os.path.join(results_dir, "plots")

os.makedirs(data_dest, exist_ok=True)
os.makedirs(plots_dest, exist_ok=True)

# Files to copy from C:\Diploma\permafrost_analysis\результаты
res_files = [
    'lena_lag.csv',
    'water_level_peak_lags_yakutsk.csv',
    'water_level_peak_lags_якутск.csv',
    'anomaly_chs_linked.csv',
    'water_level_monthly_corr.csv',
    'mchs_events.csv',
    'mchs_events_lena_bank.csv',
    'daily_anomalies_operational.csv',
    'monthly_anomalies_operational.csv',
    'water_level_annual_features.csv',
    'scenario_annual.csv'
]

print("=== COPYING DATA TABLES TO RESULTS ===")
for f in res_files:
    src = os.path.join(base_dir, "результаты", f)
    if os.path.exists(src):
        dst = os.path.join(data_dest, f)
        shutil.copy2(src, dst)
        print(f"Copied: {f} -> RESULTS/data_tables/")

# Files to copy from C:\Diploma\permafrost_analysis\data
plot_files = [
    'anomalies_overview.png',
    'lena_lag.png',
    'water_chs_link_by_year.png',
    'water_level_peak_lags_yakutsk.png',
    'water_level_peak_lags_якутск.png',
    'water_level_spring_peaks.png'
]

print("\n=== COPYING PLOTS TO RESULTS ===")
for f in plot_files:
    src = os.path.join(base_dir, "data", f)
    if os.path.exists(src):
        dst = os.path.join(plots_dest, f)
        shutil.copy2(src, dst)
        print(f"Copied: {f} -> RESULTS/plots/")

# Also copy СТС.csv from C:\Diploma\permafrost_analysis\data to data_tables
src_ctc = os.path.join(base_dir, "data", "СТС.csv")
if os.path.exists(src_ctc):
    dst_ctc = os.path.join(data_dest, "СТС.csv")
    shutil.copy2(src_ctc, dst_ctc)
    print("Copied: СТС.csv -> RESULTS/data_tables/")
