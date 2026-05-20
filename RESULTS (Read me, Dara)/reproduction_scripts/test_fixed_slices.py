import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
data_dir = r"c:\Diploma\permafrost_analysis\data"

air_file = os.path.join(data_dir, "air", "wr373144a2", "wr373144a2.txt")

# Let's read first few lines
with open(air_file, 'r', encoding='utf-8') as f:
    lines = [f.readline().rstrip() for _ in range(5)]

# Let's try to slice the line using cumulative widths:
# WMO: 5, Year: 4, Month: 2, Day: 2, GenQ: 1, Min: 5, MinQ: 1, Mean: 5, MeanQ: 1, Max: 5, MaxQ: 1, Precip: 5, PrecipDetail: 1, PrecipQ: 1
# But wait! In the raw line, WMO is '24266' (5 chars), then there is a space, then '1885' (4 chars), then '  1' (3 chars), then '  1' (3 chars), then ' 0' (2 chars)?
# Let's see the raw indices for the first line:
# '24266 1885  1  1 0       9 -47.0 0       9       9 9'
# Let's print each character and its index:
line = lines[0]
print(f"Line length: {len(line)}")
for idx, c in enumerate(line):
    print(f"{idx:2d}: '{c}'")
