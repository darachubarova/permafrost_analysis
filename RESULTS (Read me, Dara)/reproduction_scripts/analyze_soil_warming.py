import os
import sys
import pandas as pd
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')
data_dir = r"c:\Diploma\permafrost_analysis\data"

print("=== ANALYZING DEEP SOIL WARMING ===")
soil_file = os.path.join(data_dir, "soil", "wr373144a3", "wr373144a3.txt")

# Soil columns in wr373144a3.txt:
# WMO: 0-5, Year: 6-10, Month: 11-13, Day: 14-16
# Then 12 depths. Each depth has Temp (5 chars) and Q (1 char), with a 1-char space separator.
# Depths: 2, 5, 10, 15, 20, 40, 60, 80, 120, 160, 240, 320 cm.
# Let's map depth to their indices:
# Temp 2cm: indices 19:24
# Q 2cm: index 25
# Temp 5cm: indices 27:32
# Q 5cm: index 33
# ...
# Let's write a flexible parser using split, because we saw that soil data has all columns written with 999.9 for missing values.
# Let's check if the split length is always consistent. It should be WMO (1) + Year (1) + Month (1) + Day (1) + 12 * 2 (Temp + Q) = 28 elements.
# Let's verify this!

soil_records = []
with open(soil_file, 'r', encoding='utf-8') as f:
    for line in f:
        if line.startswith('24959'): # Yakutsk
            parts = line.strip().split()
            if len(parts) == 28:
                try:
                    year = int(parts[1])
                    month = int(parts[2])
                    day = int(parts[3])
                    
                    # Depths: 120cm is index 8 (which is parts[4 + 8*2] = parts[20])
                    # 160cm is index 9 (parts[4 + 9*2] = parts[22])
                    # 240cm is index 10 (parts[4 + 10*2] = parts[24])
                    # 320cm is index 11 (parts[4 + 11*2] = parts[26])
                    
                    t120 = float(parts[20]) if parts[20] != '999.9' else np.nan
                    t160 = float(parts[22]) if parts[22] != '999.9' else np.nan
                    t240 = float(parts[24]) if parts[24] != '999.9' else np.nan
                    t320 = float(parts[26]) if parts[26] != '999.9' else np.nan
                    
                    soil_records.append({
                        'year': year, 'month': month, 'day': day,
                        't120': t120, 't160': t160, 't240': t240, 't320': t320
                    })
                except Exception as e:
                    pass

df_soil = pd.DataFrame(soil_records)
print(f"Parsed {len(df_soil)} daily soil temperature records for Yakutsk.")

# Compute annual mean temperatures
annual_soil = []
for yr in sorted(df_soil['year'].unique()):
    df_yr = df_soil[df_soil['year'] == yr]
    
    # We want years with a good amount of data (e.g. > 250 days)
    row_data = {'year': yr}
    valid = True
    for col in ['t120', 't160', 't240', 't320']:
        df_col = df_yr[df_yr[col].notna()]
        if len(df_col) < 250:
            row_data[col] = np.nan
            valid = False
        else:
            row_data[col] = df_col[col].mean()
            
    if valid:
        annual_soil.append(row_data)

df_annual = pd.DataFrame(annual_soil)
print(df_annual.dropna().head(10))

# Perform trend analysis for 320 cm
df_trend = df_annual.dropna(subset=['t320'])
if not df_trend.empty:
    X = df_trend['year'].values
    y = df_trend['t320'].values
    
    # Fit linear regression manually
    A = np.column_stack([np.ones(len(X)), X])
    w, _, _, _ = np.linalg.lstsq(A, y, rcond=None)
    
    slope = w[1]
    intercept = w[0]
    
    print(f"\nLong-Term warming trend at 320 cm depth (1964-2024):")
    print(f"  Linear regression: T_320 = {slope:.5f} * Year + {intercept:.2f}")
    print(f"  Warming rate: {slope * 10:.3f}°C per decade")
    
    # Check warming over specific decades: 1970s vs 2010s
    t_1970 = df_trend[(df_trend['year'] >= 1970) & (df_trend['year'] <= 1979)]['t320'].mean()
    t_2010 = df_trend[(df_trend['year'] >= 2010) & (df_trend['year'] <= 2019)]['t320'].mean()
    print(f"  Average T_320 in 1970s: {t_1970:.3f}°C")
    print(f"  Average T_320 in 2010s: {t_2010:.3f}°C")
    print(f"  Total observed warming in 40 years: {t_2010 - t_1970:+.3f}°C")
