import os
import sys
import pandas as pd
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')
data_dir = r"c:\Diploma\permafrost_analysis\data"

print("=== STEP 1: PARSING AIR TEMPERATURE ===")
air_file = os.path.join(data_dir, "air", "wr373144a2", "wr373144a2.txt")
air_data = []

# Fields in air: WMO: 5, Year: 4, Month: 2, Day: 2, GenQ: 1, Min: 5, MinQ: 1, Mean: 5, MeanQ: 1, Max: 5, MaxQ: 1, Precip: 5, PrecipDetail: 1, PrecipQ: 1
with open(air_file, 'r', encoding='utf-8') as f:
    for line in f:
        if line.startswith('24959'): # Yakutsk
            try:
                wmo = line[0:5].strip()
                year = int(line[6:10].strip())
                month = int(line[11:13].strip())
                day = int(line[14:16].strip())
                
                # Mean temperature
                mean_t_str = line[27:32].strip()
                if mean_t_str and mean_t_str != '99.9' and mean_t_str != '999.9':
                    mean_t = float(mean_t_str)
                else:
                    mean_t = np.nan
                
                # Precip
                precip_str = line[43:48].strip()
                if precip_str and precip_str != '99.9' and precip_str != '999.9':
                    precip = float(precip_str)
                else:
                    precip = 0.0
                    
                air_data.append({
                    'year': year, 'month': month, 'day': day, 'tmean': mean_t, 'precip': precip
                })
            except Exception as e:
                pass

df_air = pd.DataFrame(air_data)
print(f"Parsed {len(df_air)} daily weather records for Yakutsk.")

print("\n=== STEP 2: PARSING SNOW DEPTH ===")
snow_file = os.path.join(data_dir, "snow", "wr373144a5", "wr373144a5.txt")
snow_data = []

with open(snow_file, 'r', encoding='utf-8') as f:
    for line in f:
        if line.startswith('24959'): # Yakutsk
            try:
                wmo = line[0:5].strip()
                year = int(line[6:10].strip())
                month = int(line[11:13].strip())
                day = int(line[14:16].strip())
                
                height_str = line[17:21].strip()
                if height_str and height_str != '9999':
                    height = float(height_str)
                else:
                    height = 0.0
                
                snow_data.append({
                    'year': year, 'month': month, 'day': day, 'snow_height': height
                })
            except Exception as e:
                pass

df_snow = pd.DataFrame(snow_data)
print(f"Parsed {len(df_snow)} daily snow records for Yakutsk.")

print("\n=== STEP 3: COMPUTING ANNUAL CLIMATE FEATURES ===")
annual_features = []
years = sorted(df_air['year'].unique())

for yr in range(2005, 2026):
    df_yr = df_air[df_air['year'] == yr]
    if len(df_yr[df_yr['tmean'].notna()]) < 300:
        continue
        
    ddt = df_yr[df_yr['tmean'] > 0]['tmean'].sum()
    precip_summer = df_yr[(df_yr['month'] >= 5) & (df_yr['month'] <= 9)]['precip'].sum()
    
    # DDF: winter season
    df_prev = df_air[df_air['year'] == yr - 1]
    winter_t_prev = df_prev[df_prev['month'] >= 10]['tmean'].values
    winter_t_curr = df_yr[df_yr['month'] <= 4]['tmean'].values
    winter_temps = np.concatenate([winter_t_prev, winter_t_curr])
    ddf = np.abs(winter_temps[winter_temps < 0]).sum() if len(winter_temps) > 0 else np.nan
    
    # Snow
    df_snow_prev = df_snow[df_snow['year'] == yr - 1]
    snow_prev = df_snow_prev[df_snow_prev['month'] >= 11]['snow_height'].values
    snow_curr = df_snow[(df_snow['year'] == yr) & (df_snow['month'] <= 3)]['snow_height'].values
    snow_winter = np.concatenate([snow_prev, snow_curr])
    avg_snow = np.mean(snow_winter) if len(snow_winter) > 0 else 0.0
    
    annual_features.append({
        'year': yr,
        'DDT': ddt,
        'DDF': ddf,
        'precip_summer': precip_summer,
        'avg_snow_winter': avg_snow
    })

df_features = pd.DataFrame(annual_features)
print(df_features.head())

print("\n=== STEP 4: MERGING WITH ALT DATA AND TRAINING MODEL ===")
ctc_df = pd.read_csv(os.path.join(data_dir, "СТС.csv"), encoding='utf-8')

# Get R42 (Tuymada)
r42_row = ctc_df[ctc_df['Site Code'] == 'R42'].iloc[0]
r42_alt = []
for col in ctc_df.columns:
    if col.isdigit():
        val = r42_row[col]
        if pd.notna(val) and val != 'inactive':
            r42_alt.append({'year': int(col), 'ALT': float(val)})
df_r42 = pd.DataFrame(r42_alt)

# Get R43 (Neleger)
r43_row = ctc_df[ctc_df['Site Code'] == 'R43'].iloc[0]
r43_alt = []
for col in ctc_df.columns:
    if col.isdigit():
        val = r43_row[col]
        if pd.notna(val) and val != 'inactive':
            r43_alt.append({'year': int(col), 'ALT': float(val)})
df_r43 = pd.DataFrame(r43_alt)

# Merge
df_model_42 = pd.merge(df_r42, df_features, on='year')
df_model_43 = pd.merge(df_r43, df_features, on='year')

print(f"\nSite R42 merged records: {len(df_model_42)}")
print(f"Site R43 merged records: {len(df_model_43)}")

def train_and_eval(df, name):
    # Features
    X_cols = ['DDT', 'DDF', 'avg_snow_winter', 'precip_summer']
    X = df[X_cols].values
    y = df['ALT'].values
    
    # Add intercept column
    X_design = np.column_stack([np.ones(X.shape[0]), X])
    
    # Least squares solver
    w, residuals, rank, s = np.linalg.lstsq(X_design, y, rcond=None)
    
    # Predict
    y_pred = X_design @ w
    
    # R2
    y_mean = np.mean(y)
    ss_tot = np.sum((y - y_mean)**2)
    ss_res = np.sum((y - y_pred)**2)
    r2 = 1 - (ss_res / ss_tot)
    
    # MAE
    mae = np.mean(np.abs(y - y_pred))
    
    print(f"\n--- Model for {name} ---")
    print(f"R2 Score: {r2:.4f}")
    print(f"MAE: {mae:.2f} cm")
    print("Coefficients:")
    print(f"  Intercept (b): {w[0]:.4f}")
    for col, coef in zip(X_cols, w[1:]):
        print(f"  {col}: {coef:.4f}")
        
    print("\nActual vs Predicted ALT:")
    for idx, row in df.iterrows():
        # calculate prediction manually
        feat = np.array([1, row['DDT'], row['DDF'], row['avg_snow_winter'], row['precip_summer']])
        pred = feat @ w
        print(f"  Year {row['year']:.0f}: Actual = {row['ALT']:.1f} cm, Predicted = {pred:.1f} cm (Error = {row['ALT'] - pred:.1f} cm)")

if len(df_model_42) > 0:
    train_and_eval(df_model_42, "Tuymada (R42, Yakutsk region)")
if len(df_model_43) > 0:
    train_and_eval(df_model_43, "Neleger (R43, Yakutsk region)")
