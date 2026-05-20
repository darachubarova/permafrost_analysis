import os
import sys
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

data_dir = r"c:\Diploma\permafrost_analysis\data"

print("=== INSPECTING CТС.csv ===")
ctc_df = pd.read_csv(os.path.join(data_dir, "СТС.csv"), encoding='utf-8')
print("Shape:", ctc_df.shape)
print("Unique Regions:", ctc_df['Region'].unique().tolist())
print("First 5 rows of metadata:")
print(ctc_df[['Site Code', 'Region', 'Site Name', 'LAT', 'LONG', 'Method']].head(5))

print("\n=== INSPECTING fld FILE DETAILS ===")
for sub, fld_name in [('soil', 'fld373144a3.txt'), ('air', 'fld373144a2.txt'), ('snow', 'fld373144a5.txt')]:
    fpath = os.path.join(data_dir, sub, sub.replace('soil', 'wr373144a3').replace('air', 'wr373144a2').replace('snow', 'wr373144a5'), fld_name)
    print(f"\n{sub} field definitions ({fld_name}):")
    if os.path.exists(fpath):
        with open(fpath, 'r', encoding='cp1251', errors='ignore') as f:
            for line in f:
                print(f"  {line.strip()}")

print("\n=== INSPECTING CALM_Summary_table.xls ===")
calm_path = os.path.join(data_dir, "CALM_Summary_table.xls")
if os.path.exists(calm_path):
    xl = pd.ExcelFile(calm_path)
    print("Sheets:", xl.sheet_names)
    for sheet in xl.sheet_names[:2]:
        df = xl.parse(sheet, nrows=3)
        print(f"Sheet: {sheet}, columns:", df.columns.tolist()[:10])
        print(df.head(2))

print("\n=== INSPECTING baza-dla-interneta-1991-2024-gg.xls ===")
baza_path = os.path.join(data_dir, "baza-dla-interneta-1991-2024-gg.xls")
if os.path.exists(baza_path):
    xl = pd.ExcelFile(baza_path)
    print("Sheets:", xl.sheet_names)
    for sheet in xl.sheet_names[:3]:
        df = xl.parse(sheet, nrows=3)
        print(f"Sheet: {sheet}, columns:", df.columns.tolist()[:10])
        print(df.head(2))
