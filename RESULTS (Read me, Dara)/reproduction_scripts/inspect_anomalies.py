import os
import sys
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

data_dir = r"c:\Diploma\permafrost_analysis\data"

print("=== INSPECTING DAILY ANOMALIES ===")
daily_path = os.path.join(data_dir, "daily_anomalies_operational.csv")
if os.path.exists(daily_path):
    df_daily = pd.read_csv(daily_path, encoding='utf-8')
    print("Shape:", df_daily.shape)
    print("Stations:", df_daily['station_name'].unique().tolist())
    print("Date range:", df_daily['date'].min(), "to", df_daily['date'].max())
    print("Unique Signals:")
    print(df_daily['signals'].value_counts().head(10))
    print("Severity distribution:")
    print(df_daily['severity'].value_counts())

print("\n=== INSPECTING MONTHLY ANOMALIES ===")
monthly_path = os.path.join(data_dir, "monthly_anomalies_operational.csv")
if os.path.exists(monthly_path):
    df_monthly = pd.read_csv(monthly_path, encoding='utf-8')
    print("Shape:", df_monthly.shape)
    print("Date range:", df_monthly['period'].min(), "to", df_monthly['period'].max())
    print("Unique Signals:")
    print(df_monthly['signals'].value_counts().head(10))
    print("Severity distribution:")
    print(df_monthly['severity'].value_counts())

print("\n=== INSPECTING MCHS EVENTS ===")
mchs_path = os.path.join(data_dir, "mchs_events.csv")
if os.path.exists(mchs_path):
    df_mchs = pd.read_csv(mchs_path, encoding='utf-8')
    print("Shape:", df_mchs.shape)
    print("Unique emergency types (type_chs):")
    print(df_mchs['type_chs'].value_counts())
    print("Regions:")
    print(df_mchs['region'].value_counts())
    print("Sample rows:")
    print(df_mchs.head(10).to_string(index=False))

print("\n=== INSPECTING MCHS EVENTS LENA BANK ===")
mchs_lena_path = os.path.join(data_dir, "mchs_events_lena_bank.csv")
if os.path.exists(mchs_lena_path):
    df_mchs_lena = pd.read_csv(mchs_lena_path, encoding='utf-8')
    print("Shape:", df_mchs_lena.shape)
    print("Unique emergency types (type_chs):")
    print(df_mchs_lena['type_chs'].value_counts())
    print("Sample rows:")
    print(df_mchs_lena.head(10).to_string(index=False))
