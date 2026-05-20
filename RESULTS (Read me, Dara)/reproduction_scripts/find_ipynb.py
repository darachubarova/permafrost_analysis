import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
base_dir = r"C:\Diploma\permafrost_analysis"

print("=== SEARCHING FOR IPYNB FILES ===")
for root, dirs, files in os.walk(base_dir):
    for f in files:
        if f.endswith('.ipynb'):
            print(f"Found: {os.path.join(root, f)}")

print("\n=== SEARCHING FOR DARA FOLDER ===")
for root, dirs, files in os.walk(base_dir):
    for d in dirs:
        if 'dara' in d.lower():
            print(f"Found dir: {os.path.join(root, d)}")
