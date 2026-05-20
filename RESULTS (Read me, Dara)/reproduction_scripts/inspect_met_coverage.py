import os
import sys
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

data_dir = r"c:\Diploma\permafrost_analysis\data"

stations = {
    24266: 'Verkhoyansk',
    24343: 'Zhigansk',
    24688: 'Oymyakon',
    24944: 'Olekminsk',
    24959: 'Yakutsk'
}

def parse_line(line):
    # Split by whitespace, ignore empty elements
    parts = line.strip().split()
    return parts

print("=== CHECKING AIR TEMPERATURE FILE ===")
air_file = os.path.join(data_dir, "air", "wr373144a2", "wr373144a2.txt")
air_counts = {st: 0 for st in stations}
air_years = {st: set() for st in stations}
if os.path.exists(air_file):
    with open(air_file, 'r', encoding='utf-8') as f:
        for _ in range(100):
            line = f.readline()
            if not line:
                break
            parts = parse_line(line)
            if len(parts) >= 4:
                try:
                    wmo = int(parts[0])
                    year = int(parts[1])
                    if wmo in stations:
                        air_counts[wmo] += 1
                        air_years[wmo].add(year)
                except ValueError:
                    pass
    
    # Let's read the whole file to count records and check year ranges
    # Since the file is 14 MB, reading it line-by-line is fast in Python
    air_counts = {st: 0 for st in stations}
    air_years = {st: [] for st in stations}
    with open(air_file, 'r', encoding='utf-8') as f:
        for line in f:
            parts = parse_line(line)
            if len(parts) >= 4:
                try:
                    wmo = int(parts[0])
                    year = int(parts[1])
                    if wmo in stations:
                        air_counts[wmo] += 1
                        air_years[wmo].append(year)
                except ValueError:
                    pass
    for wmo, st_name in stations.items():
        yrs = air_years[wmo]
        if yrs:
            print(f"Station: {st_name} ({wmo}) - Records: {air_counts[wmo]}, Years: {min(yrs)} to {max(yrs)}")
        else:
            print(f"Station: {st_name} ({wmo}) - No records found!")

print("\n=== CHECKING SOIL TEMPERATURE FILE ===")
soil_file = os.path.join(data_dir, "soil", "wr373144a3", "wr373144a3.txt")
soil_counts = {st: 0 for st in stations}
soil_years = {st: [] for st in stations}
if os.path.exists(soil_file):
    with open(soil_file, 'r', encoding='utf-8') as f:
        for line in f:
            parts = parse_line(line)
            if len(parts) >= 4:
                try:
                    wmo = int(parts[0])
                    year = int(parts[1])
                    if wmo in stations:
                        soil_counts[wmo] += 1
                        soil_years[wmo].append(year)
                except ValueError:
                    pass
    for wmo, st_name in stations.items():
        yrs = soil_years[wmo]
        if yrs:
            print(f"Station: {st_name} ({wmo}) - Records: {soil_counts[wmo]}, Years: {min(yrs)} to {max(yrs)}")
        else:
            print(f"Station: {st_name} ({wmo}) - No records found!")

print("\n=== CHECKING SNOW DEPTH FILE ===")
snow_file = os.path.join(data_dir, "snow", "wr373144a5", "wr373144a5.txt")
snow_counts = {st: 0 for st in stations}
snow_years = {st: [] for st in stations}
if os.path.exists(snow_file):
    with open(snow_file, 'r', encoding='utf-8') as f:
        for line in f:
            parts = parse_line(line)
            if len(parts) >= 4:
                try:
                    wmo = int(parts[0])
                    year = int(parts[1])
                    if wmo in stations:
                        snow_counts[wmo] += 1
                        snow_years[wmo].append(year)
                except ValueError:
                    pass
    for wmo, st_name in stations.items():
        yrs = snow_years[wmo]
        if yrs:
            print(f"Station: {st_name} ({wmo}) - Records: {snow_counts[wmo]}, Years: {min(yrs)} to {max(yrs)}")
        else:
            print(f"Station: {st_name} ({wmo}) - No records found!")
