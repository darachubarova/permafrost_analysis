import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
data_dir = r"c:\Diploma\permafrost_analysis\data"

print("=== SAMPLE AIR DATA FOR YAKUTSK (24959) ===")
air_file = os.path.join(data_dir, "air", "wr373144a2", "wr373144a2.txt")
count = 0
with open(air_file, 'r', encoding='utf-8') as f:
    for line in f:
        if line.startswith('24959'):
            # Find a line with some non-empty/non-missing temperature values
            parts = line.strip().split()
            # If mean air temp is not missing (usually represented as 99.9 or similar? let's see)
            # In the columns list: 0: WMO, 1: Year, 2: Month, 3: Day, 4: Quality, 5: Min, 6: Q_Min, 7: Mean, 8: Q_Mean, 9: Max, 10: Q_Max, 11: Precip, 12: Precip_detail, 13: Q_Precip
            if len(parts) >= 12:
                # print a few rows
                print(f"Row: {parts}")
                count += 1
                if count >= 5:
                    break

print("\n=== SAMPLE SOIL DATA FOR YAKUTSK (24959) ===")
soil_file = os.path.join(data_dir, "soil", "wr373144a3", "wr373144a3.txt")
count = 0
with open(soil_file, 'r', encoding='utf-8') as f:
    for line in f:
        if line.startswith('24959'):
            parts = line.strip().split()
            # soil depths: 2, 5, 10, 15, 20, 40, 60, 80, 120, 160, 240, 320 cm
            # look for a line where the deeper soil temps (e.g. 160 or 320 cm) are not 999.9
            if len(parts) >= 10:
                # check if there's any non 999.9 value
                has_data = any(p != '999.9' for p in parts[4::2])
                if has_data:
                    print(f"Row: {parts}")
                    count += 1
                    if count >= 5:
                        break

print("\n=== SAMPLE SNOW DATA FOR YAKUTSK (24959) ===")
snow_file = os.path.join(data_dir, "snow", "wr373144a5", "wr373144a5.txt")
count = 0
with open(snow_file, 'r', encoding='utf-8') as f:
    for line in f:
        if line.startswith('24959'):
            parts = line.strip().split()
            # 0: WMO, 1: Year, 2: Month, 3: Day, 4: Snow height (9999 for missing, or actual height in cm)
            if len(parts) >= 5 and parts[4] != '9999' and int(parts[4]) > 10:
                print(f"Row: {parts}")
                count += 1
                if count >= 5:
                    break
