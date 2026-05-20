import os
import sys
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

data_dir = r"c:\Diploma\permafrost_analysis\data"
ctc_df = pd.read_csv(os.path.join(data_dir, "СТС.csv"), encoding='utf-8')

# Let's inspect R42 and R43
target_sites = ctc_df[ctc_df['Site Code'].isin(['R42', 'R43'])]
print("=== SITES R42 & R43 ===")
for idx, row in target_sites.iterrows():
    print(f"\nSite: {row['Site Code']} - {row['Site Name']}")
    print(f"Lat: {row['LAT']}, Lon: {row['LONG']}, Method: {row['Method']}")
    # print years that are not null
    years_data = {}
    for col in ctc_df.columns:
        if col.isdigit():
            val = row[col]
            if pd.notna(val) and val != 'inactive':
                years_data[col] = val
    print(f"Data available for {len(years_data)} years:")
    # sort by year
    sorted_years = sorted(years_data.keys())
    for yr in sorted_years:
        print(f"  {yr}: {years_data[yr]} cm")

print("\n=== SUMMARY OF ALL YAKUTIA SITES ===")
# find all sites where region is North East Siberia or Central Siberia or name contains Yakutsk
yakutia_all = ctc_df[ctc_df['Site Name'].str.contains('Yakutsk|Neleger|Tuymada|Lena', case=False, na=False) | ctc_df['Region'].isin(['North East Siberia', 'Central Siberia'])]
print(f"Found {len(yakutia_all)} sites in Yakutia region:")
for idx, row in yakutia_all.iterrows():
    # count non-null years
    non_null_count = 0
    for col in ctc_df.columns:
        if col.isdigit():
            val = row[col]
            if pd.notna(val) and val != 'inactive' and val != 'nan' and val != '':
                non_null_count += 1
    print(f"  Code: {row['Site Code']}, Name: {row['Site Name']}, Lat: {row['LAT']:.3f}, Lon: {row['LONG']:.3f}, Years with data: {non_null_count}")
