import os
import sys
import pandas as pd
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')
data_dir = r"c:\Diploma\permafrost_analysis\data"

print("=== CALCULATING CLIMATE FEATURES ===")
air_file = os.path.join(data_dir, "air", "wr373144a2", "wr373144a2.txt")
snow_file = os.path.join(data_dir, "snow", "wr373144a5", "wr373144a5.txt")

# Read Air for Yakutsk
air_data = []
with open(air_file, 'r', encoding='utf-8') as f:
    for line in f:
        if line.startswith('24959'):
            try:
                year = int(line[6:10].strip())
                month = int(line[11:13].strip())
                mean_t_str = line[27:32].strip()
                if mean_t_str and mean_t_str != '99.9' and mean_t_str != '999.9':
                    mean_t = float(mean_t_str)
                    air_data.append({'year': year, 'month': month, 'tmean': mean_t})
            except:
                pass
df_air = pd.DataFrame(air_data)

# Read Snow for Yakutsk
snow_data = []
with open(snow_file, 'r', encoding='utf-8') as f:
    for line in f:
        if line.startswith('24959'):
            try:
                year = int(line[6:10].strip())
                month = int(line[11:13].strip())
                h_str = line[17:21].strip()
                if h_str and h_str != '9999':
                    height = float(h_str)
                    snow_data.append({'year': year, 'month': month, 'snow_height': height})
            except:
                pass
df_snow = pd.DataFrame(snow_data)

# Annual features
annual = []
for yr in range(2005, 2026):
    df_yr_t = df_air[df_air['year'] == yr]
    # completeness check
    if len(df_yr_t[df_yr_t['tmean'].notna()]) < 300:
        continue
    
    ddt = df_yr_t[df_yr_t['tmean'] > 0]['tmean'].sum()
    
    # Snow
    df_snow_prev = df_snow[df_snow['year'] == yr - 1]
    snow_prev = df_snow_prev[df_snow_prev['month'] >= 11]['snow_height'].values
    snow_curr = df_snow[(df_snow['year'] == yr) & (df_snow['month'] <= 3)]['snow_height'].values
    snow_winter = np.concatenate([snow_prev, snow_curr])
    avg_snow = np.mean(snow_winter) if len(snow_winter) > 0 else 0.0
    
    annual.append({'year': yr, 'DDT': ddt, 'avg_snow_winter': avg_snow})
df_features = pd.DataFrame(annual)

# Load ALT for R42 and R43
ctc_df = pd.read_csv(os.path.join(data_dir, "СТС.csv"), encoding='utf-8')

for code, name in [('R42', 'Tuymada (R42)'), ('R43', 'Neleger (R43)')]:
    row = ctc_df[ctc_df['Site Code'] == code].iloc[0]
    alt_data = []
    for col in ctc_df.columns:
        if col.isdigit():
            val = row[col]
            if pd.notna(val) and val != 'inactive':
                alt_data.append({'year': int(col), 'ALT': float(val)})
    df_alt = pd.DataFrame(alt_data)
    
    # Merge
    df_m = pd.merge(df_alt, df_features, on='year')
    if df_m.empty:
        continue
        
    print(f"\n=== CALIBRATING STEFAN MODEL FOR {name} ===")
    
    # Model 1: Classic Stefan ALT = E * sqrt(DDT)
    df_m['sqrt_DDT'] = np.sqrt(df_m['DDT'])
    E_vals = df_m['ALT'] / df_m['sqrt_DDT']
    E_mean = np.mean(E_vals)
    E_std = np.std(E_vals)
    print(f"Classic Stefan Coefficient (E): {E_mean:.4f} (std: {E_std:.4f}, CoV: {E_std/E_mean:.4f})")
    
    # Evaluate classic model
    pred_classic = E_mean * df_m['sqrt_DDT']
    mae_classic = np.mean(np.abs(df_m['ALT'] - pred_classic))
    r2_classic = 1 - np.sum((df_m['ALT'] - pred_classic)**2) / np.sum((df_m['ALT'] - np.mean(df_m['ALT']))**2)
    print(f"  Classic Model R2: {r2_classic:.4f}, MAE: {mae_classic:.2f} cm")
    
    # Model 2: Hybrid Stefan with Snow Correction: ALT = E_base * sqrt(DDT) * (1 + beta * H_snow)
    y_reg = df_m['ALT'] / df_m['sqrt_DDT']
    X_reg = df_m['avg_snow_winter'].values
    X_design = np.column_stack([np.ones(len(X_reg)), X_reg])
    w, _, _, _ = np.linalg.lstsq(X_design, y_reg, rcond=None)
    
    a, b = w[0], w[1]
    E_base = a
    beta = b / a if a != 0 else 0
    
    # Evaluate hybrid model
    pred_hybrid = E_base * df_m['sqrt_DDT'] * (1 + beta * df_m['avg_snow_winter'])
    mae_hybrid = np.mean(np.abs(df_m['ALT'] - pred_hybrid))
    r2_hybrid = 1 - np.sum((df_m['ALT'] - pred_hybrid)**2) / np.sum((df_m['ALT'] - np.mean(df_m['ALT']))**2)
    
    print(f"Hybrid Stefan Model (with Snow Correction):")
    print(f"  E_base (Soil factor): {E_base:.4f}")
    print(f"  Beta (Snow insulating sensitivity): {beta:.5f}")
    print(f"  Hybrid Model R2: {r2_hybrid:.4f}, MAE: {mae_hybrid:.2f} cm")
    
    # Print comparison
    print("\nYear  Actual_ALT  Classic_Pred (Error)  Hybrid_Pred (Error)")
    for idx, r in df_m.iterrows():
        pc = E_mean * np.sqrt(r['DDT'])
        ph = E_base * np.sqrt(r['DDT']) * (1 + beta * r['avg_snow_winter'])
        print(f"{r['year']:.0f}   {r['ALT']:.1f} cm   {pc:.1f} cm ({r['ALT']-pc:+.1f})    {ph:.1f} cm ({r['ALT']-ph:+.1f})")
