import os
import sys
import pandas as pd
import glob

# Ensure stdout handles UTF-8 correctly
sys.stdout.reconfigure(encoding='utf-8')

data_dir = r"c:\Diploma\permafrost_analysis\data"

def try_read_text(file_path, num_lines=5):
    encodings = ['utf-8', 'cp1251', 'latin1', 'utf-16']
    for enc in encodings:
        try:
            with open(file_path, 'r', encoding=enc) as f:
                lines = [f.readline().strip() for _ in range(num_lines)]
            return enc, lines
        except UnicodeDecodeError:
            continue
    # If all fail, read as binary
    with open(file_path, 'rb') as f:
        lines = [f.readline().strip() for _ in range(num_lines)]
    return 'binary', lines

def try_read_csv(file_path, num_rows=5):
    encodings = ['utf-8', 'cp1251', 'latin-1']
    for enc in encodings:
        try:
            df = pd.read_csv(file_path, encoding=enc, nrows=num_rows)
            return enc, df
        except Exception:
            continue
    return None, None

print("=== EXPLORING MAIN DATA DIRECTORY ===")
for item in os.listdir(data_dir):
    full_path = os.path.join(data_dir, item)
    if os.path.isfile(full_path):
        print(f"\nFile: {item}, Size: {os.path.getsize(full_path)} bytes")
        if item.endswith('.csv'):
            enc, df = try_read_csv(full_path)
            if df is not None:
                print(f"  Encoding: {enc}")
                print(f"  Columns: {df.columns.tolist()}")
                print(f"  First 2 rows:\n{df.head(2).to_string(index=False)}")
            else:
                print("  Failed to read as CSV with common encodings.")
        elif item.endswith('.xls') or item.endswith('.xlsx'):
            try:
                xl = pd.ExcelFile(full_path)
                print(f"  Sheets: {xl.sheet_names}")
                df = xl.parse(xl.sheet_names[0], nrows=5)
                print(f"  Columns: {df.columns.tolist()}")
                print(f"  First 2 rows:\n{df.head(2).to_string(index=False)}")
            except Exception as e:
                print(f"  Error reading Excel: {e}")

print("\n=== EXPLORING SOIL, AIR, SNOW DIRECTORIES ===")
for sub in ['soil', 'air', 'snow']:
    sub_path = os.path.join(data_dir, sub)
    if os.path.exists(sub_path):
        print(f"\nSubdirectory: {sub}")
        subdirs = [d for d in os.listdir(sub_path) if os.path.isdir(os.path.join(sub_path, d))]
        for sd in subdirs:
            sd_path = os.path.join(sub_path, sd)
            print(f"  Folder: {sd}")
            for f in os.listdir(sd_path):
                f_path = os.path.join(sd_path, f)
                if f.endswith('.txt'):
                    enc, lines = try_read_text(f_path)
                    print(f"    File: {f}, Encoding: {enc}, Size: {os.path.getsize(f_path)} bytes")
                    print("    First 5 lines:")
                    for l in lines:
                        print(f"      {l}")

print("\n=== EXPLORING HYDRO DIRECTORY ===")
hydro_path = os.path.join(data_dir, 'hydro')
if os.path.exists(hydro_path):
    hydro_files = glob.glob(os.path.join(hydro_path, "*.csv"))
    print(f"Found {len(hydro_files)} hydro files.")
    if hydro_files:
        f_path = hydro_files[0]
        enc, df = try_read_csv(f_path)
        if df is not None:
            print(f"  File: {os.path.basename(f_path)}, Encoding: {enc}")
            print(f"  Columns: {df.columns.tolist()}")
            print(f"  First 3 rows:\n{df.head(3)}")
        else:
            print(f"  Failed to read {os.path.basename(f_path)} as CSV.")
