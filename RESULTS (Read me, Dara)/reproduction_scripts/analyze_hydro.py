import os
import sys
import pandas as pd
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')
data_dir = r"c:\Diploma\permafrost_analysis\data"
hydro_dir = os.path.join(data_dir, "hydro")

# Stations in downstream order
stations_order = [
    'kirensk', 'vitim', 'lensk', 'olekminsk', 'pokrovsk', 'tabaga', 'yakutsk', 'sangar', 'zhigansk'
]

print("=== PARSING HYDRO DATA ===")
station_peaks = {}

for st in stations_order:
    fpath = os.path.join(hydro_dir, f"lena-{st}.csv")
    if os.path.exists(fpath):
        # The file has columns Date;Value. Semicolon-separated.
        try:
            df = pd.read_csv(fpath, sep=';', parse_dates=['Date'])
            df.columns = ['Date', 'Value']
            # Clean Value (convert to float, dropna)
            df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
            df = df.dropna()
            
            # Find the peak during spring break-up (typically May 1 to June 30) for each year
            df['Year'] = df['Date'].dt.year
            df['Month'] = df['Date'].dt.month
            
            # Filter for May-June
            df_spring = df[(df['Month'] == 5) | (df['Month'] == 6)]
            
            peaks = []
            for yr, group in df_spring.groupby('Year'):
                if len(group) > 15: # need a reasonable number of observations
                    idx_max = group['Value'].idxmax()
                    row_max = group.loc[idx_max]
                    peaks.append({
                        'year': yr,
                        'peak_date': row_max['Date'],
                        'peak_value': row_max['Value']
                    })
            station_peaks[st] = pd.DataFrame(peaks)
            print(f"Station {st.capitalize()}: Found peaks for {len(peaks)} years (e.g. {peaks[0]['year']} to {peaks[-1]['year'] if peaks else ''})")
        except Exception as e:
            print(f"Error parsing {st}: {e}")

print("\n=== ANALYZING PEAK PROPAGATION LAGS (VS YAKUTSK) ===")
# Let's align peak dates between stations to see how many days it takes for the peak to travel
# Yakutsk is our reference point for Central Yakutia
df_y = station_peaks.get('yakutsk')
if df_y is not None:
    for st in ['lensk', 'olekminsk', 'tabaga', 'sangar', 'zhigansk']:
        df_st = station_peaks.get(st)
        if df_st is not None:
            # Merge on year
            df_m = pd.merge(df_y, df_st, on='year', suffixes=('_yakutsk', f'_{st}'))
            if not df_m.empty:
                # Calculate lag in days: Date(st) - Date(Yakutsk)
                # For upstream stations (lensk, olekminsk, tabaga), peak_date_st should be BEFORE peak_date_yakutsk, so lag = Yakutsk - st
                # For downstream stations (sangar, zhigansk), peak_date_st should be AFTER peak_date_yakutsk, so lag = st - Yakutsk
                if st in ['lensk', 'olekminsk', 'tabaga']:
                    lags = (df_m['peak_date_yakutsk'] - df_m[f'peak_date_{st}']).dt.days
                    dir_str = "upstream"
                else:
                    lags = (df_m[f'peak_date_{st}'] - df_m['peak_date_yakutsk']).dt.days
                    dir_str = "downstream"
                
                print(f"Peak lag between {st.capitalize()} ({dir_str}) and Yakutsk:")
                print(f"  Average lag: {np.mean(lags):.1f} days (std: {np.std(lags):.1f} days, range: {np.min(lags)} to {np.max(lags)} days)")

print("\n=== CORRELATING PEAKS WITH MCHS EMERGENCY EVENTS ===")
mchs_path = os.path.join(data_dir, "mchs_events_lena_bank.csv")
if os.path.exists(mchs_path) and 'yakutsk' in station_peaks:
    df_mchs = pd.read_csv(mchs_path, encoding='utf-8', parse_dates=['date_start'])
    # Filter for Floods and Ice Jams
    df_floods = df_mchs[df_mchs['type_chs'].isin(['Половодье', 'Затор', 'Паводок'])]
    print(f"MCHS Flood/Jam Events along Lena Bank: {len(df_floods)}")
    
    df_y_peaks = station_peaks['yakutsk']
    
    # Merge and inspect
    df_floods['year'] = df_floods['date_start'].dt.year
    df_merged = pd.merge(df_y_peaks, df_floods, on='year', how='left')
    
    print("\nYakutsk Spring Flood Peaks and MCHS Emergency Event linkage:")
    for idx, row in df_merged.iterrows():
        event_str = f"MCHS Event: {row['type_chs']} ({row['location']})" if pd.notna(row['type_chs']) else "No major emergency recorded on the bank"
        print(f"  Year {row['year']}: Peak Date = {row['peak_date'].strftime('%Y-%m-%d')}, Peak Level = {row['peak_value']:.0f} cm | {event_str}")
