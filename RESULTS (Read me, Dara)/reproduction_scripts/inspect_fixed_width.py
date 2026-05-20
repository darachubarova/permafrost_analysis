import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
data_dir = r"c:\Diploma\permafrost_analysis\data"

print("=== RAW STRING INDEX INSPECTION FOR AIR ===")
air_file = os.path.join(data_dir, "air", "wr373144a2", "wr373144a2.txt")
with open(air_file, 'r', encoding='utf-8') as f:
    for _ in range(5):
        line = f.readline()
        print(f"Raw line: '{line.rstrip()}'")
        print("Indices:  " + "".join([str(i % 10) for i in range(len(line.rstrip()))]))

print("\n=== RAW STRING INDEX INSPECTION FOR SOIL ===")
soil_file = os.path.join(data_dir, "soil", "wr373144a3", "wr373144a3.txt")
with open(soil_file, 'r', encoding='utf-8') as f:
    for _ in range(5):
        line = f.readline()
        print(f"Raw line: '{line.rstrip()}'")
        print("Indices:  " + "".join([str(i % 10) for i in range(len(line.rstrip()))]))

print("\n=== RAW STRING INDEX INSPECTION FOR SNOW ===")
snow_file = os.path.join(data_dir, "snow", "wr373144a5", "wr373144a5.txt")
with open(snow_file, 'r', encoding='utf-8') as f:
    for _ in range(5):
        line = f.readline()
        print(f"Raw line: '{line.rstrip()}'")
        print("Indices:  " + "".join([str(i % 10) for i in range(len(line.rstrip()))]))
