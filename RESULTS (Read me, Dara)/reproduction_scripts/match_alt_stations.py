import os
import sys
import pandas as pd
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

# Weather station coordinates
stations = {
    'Verkhoyansk': {'id': 24266, 'lat': 67.55, 'lon': 133.38},
    'Zhigansk': {'id': 24343, 'lat': 66.77, 'lon': 123.37},
    'Oymyakon': {'id': 24688, 'lat': 63.46, 'lon': 142.79},
    'Olekminsk': {'id': 24944, 'lat': 60.37, 'lon': 120.42},
    'Yakutsk': {'id': 24959, 'lat': 62.03, 'lon': 129.73}
}

data_dir = r"c:\Diploma\permafrost_analysis\data"
ctc_df = pd.read_csv(os.path.join(data_dir, "СТС.csv"), encoding='utf-8')

print("=== SEARCHING FOR SITES IN YAKUTIA / REPUBLIC OF SAHA ===")
yakutia_sites = ctc_df[ctc_df['Site Name'].str.contains('Yakutsk|Yakutia|Saha|Siberia|Lena|Kolyma|Vilyuy|Oymyakon|Zhigansk|Olekminsk|Verkhoyansk', case=False, na=False)]
print(f"Found {len(yakutia_sites)} sites containing Yakutsk/Siberia etc. in Site Name:")
print(yakutia_sites[['Site Code', 'Site Name', 'LAT', 'LONG', 'Method']].to_string())

print("\n=== MATCHING BY DISTANCE ===")
for st_name, coords in stations.items():
    print(f"\nStation: {st_name} (Lat: {coords['lat']}, Lon: {coords['lon']})")
    distances = []
    for idx, row in ctc_df.iterrows():
        lat_c, lon_c = row['LAT'], row['LONG']
        if pd.isna(lat_c) or pd.isna(lon_c):
            continue
        # simple Euclidean distance in degrees as a proxy for physical distance
        dist = np.sqrt((lat_c - coords['lat'])**2 + (lon_c - coords['lon'])**2)
        distances.append((dist, row['Site Code'], row['Site Name'], lat_c, lon_c))
    
    distances.sort()
    print("Top 3 closest ALT sites:")
    for dist, code, name, lat, lon in distances[:3]:
        print(f"  Code: {code}, Name: {name}, Lat: {lat:.4f}, Lon: {lon:.4f}, Distance proxy: {dist:.3f} deg")
