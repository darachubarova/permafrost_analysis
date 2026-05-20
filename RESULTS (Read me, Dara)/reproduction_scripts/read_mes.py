import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
mes_path = r"C:\Diploma\permafrost_analysis\детекция дней\месяцев.txt"

if os.path.exists(mes_path):
    with open(mes_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    print(f"File size: {len(content)} characters")
    print("Content preview (first 1000 chars):")
    print(content[:1000])
else:
    print("File does not exist")
