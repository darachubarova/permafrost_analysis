from __future__ import annotations

import calendar
from pathlib import Path

import numpy as np
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data"
PROFILE_DIR = REPO_ROOT / "RESULTS (Read me, Dara)" / "data_profiles"

STATIONS = {
    "24266": "Верхоянск",
    "24343": "Жиганск",
    "24688": "Оймякон",
    "24944": "Олёкминск",
    "24959": "Якутск",
    "30230": "Киренск",
}

SOIL_DEPTHS_CM = [2, 5, 10, 15, 20, 40, 60, 80, 120, 160, 240, 320]


def numeric_or_nan(value: str, missing: set[str]) -> float:
    value = value.strip()
    if not value or value in missing:
        return np.nan
    try:
        return float(value)
    except ValueError:
        return np.nan


def stats_row(
    source_file: str,
    parameter: str,
    values: pd.Series | list[float],
    *,
    station_id: str = "",
    station_name: str = "",
    period_start: str = "",
    period_end: str = "",
    unit: str = "",
    notes: str = "",
) -> dict[str, object]:
    series = pd.to_numeric(pd.Series(values), errors="coerce")
    valid = series.dropna()
    if valid.empty:
        summary = {
            "min": np.nan,
            "p05": np.nan,
            "median": np.nan,
            "mean": np.nan,
            "p95": np.nan,
            "max": np.nan,
            "std": np.nan,
            "iqr": np.nan,
        }
    else:
        q25 = valid.quantile(0.25)
        q75 = valid.quantile(0.75)
        summary = {
            "min": valid.min(),
            "p05": valid.quantile(0.05),
            "median": valid.median(),
            "mean": valid.mean(),
            "p95": valid.quantile(0.95),
            "max": valid.max(),
            "std": valid.std(ddof=1),
            "iqr": q75 - q25,
        }
    return {
        "source_file": source_file,
        "parameter": parameter,
        "station_id": station_id,
        "station_name": station_name,
        "period_start": period_start,
        "period_end": period_end,
        "unit": unit,
        "n_non_null": int(valid.size),
        "n_null": int(series.isna().sum()),
        **summary,
        "notes": notes,
    }


def expected_days(year: int) -> int:
    return 366 if calendar.isleap(year) else 365


def profile_air(stats: list[dict], completeness: list[dict]) -> None:
    source = DATA_DIR / "air" / "wr373144a2" / "wr373144a2.txt"
    rows = []
    with source.open(encoding="utf-8") as file:
        for line in file:
            station_id = line[0:5].strip()
            if station_id not in STATIONS:
                continue
            try:
                year = int(line[6:10].strip())
            except ValueError:
                continue
            rows.append(
                {
                    "station_id": station_id,
                    "station_name": STATIONS[station_id],
                    "year": year,
                    "tmean_degC": numeric_or_nan(line[27:32], {"99.9", "999.9"}),
                    "precip_mm": numeric_or_nan(line[43:48], {"99.9", "999.9"}),
                }
            )
    df = pd.DataFrame(rows)
    for (station_id, station_name), part in df.groupby(["station_id", "station_name"]):
        start, end = str(part["year"].min()), str(part["year"].max())
        for parameter, unit in [("tmean_degC", "degC"), ("precip_mm", "mm")]:
            stats.append(
                stats_row(
                    "data/air/wr373144a2/wr373144a2.txt",
                    parameter,
                    part[parameter],
                    station_id=station_id,
                    station_name=station_name,
                    period_start=start,
                    period_end=end,
                    unit=unit,
                    notes="Raw WMO fixed-width daily export; profile by station.",
                )
            )
        for year, yearly in part.groupby("year"):
            for col in ["tmean_degC", "precip_mm"]:
                valid = int(yearly[col].notna().sum())
                completeness.append(
                    {
                        "source_file": "data/air/wr373144a2/wr373144a2.txt",
                        "dimension": "station_year_parameter",
                        "key": f"{station_id}:{year}:{col}",
                        "expected_count": expected_days(int(year)),
                        "actual_count": valid,
                        "completeness_ratio": valid / expected_days(int(year)),
                        "notes": f"{station_name}; raw daily {col}",
                    }
                )


def profile_snow(stats: list[dict], completeness: list[dict]) -> None:
    source = DATA_DIR / "snow" / "wr373144a5" / "wr373144a5.txt"
    rows = []
    with source.open(encoding="utf-8") as file:
        for line in file:
            station_id = line[0:5].strip()
            if station_id not in STATIONS:
                continue
            try:
                year = int(line[6:10].strip())
            except ValueError:
                continue
            rows.append(
                {
                    "station_id": station_id,
                    "station_name": STATIONS[station_id],
                    "year": year,
                    "snow_depth_cm": numeric_or_nan(line[17:21], {"9999"}),
                }
            )
    df = pd.DataFrame(rows)
    for (station_id, station_name), part in df.groupby(["station_id", "station_name"]):
        stats.append(
            stats_row(
                "data/snow/wr373144a5/wr373144a5.txt",
                "snow_depth_cm",
                part["snow_depth_cm"],
                station_id=station_id,
                station_name=station_name,
                period_start=str(part["year"].min()),
                period_end=str(part["year"].max()),
                unit="cm",
                notes="Raw WMO fixed-width daily export; profile by station.",
            )
        )
        for year, yearly in part.groupby("year"):
            valid = int(yearly["snow_depth_cm"].notna().sum())
            completeness.append(
                {
                    "source_file": "data/snow/wr373144a5/wr373144a5.txt",
                    "dimension": "station_year_parameter",
                    "key": f"{station_id}:{year}:snow_depth_cm",
                    "expected_count": expected_days(int(year)),
                    "actual_count": valid,
                    "completeness_ratio": valid / expected_days(int(year)),
                    "notes": f"{station_name}; raw daily snow_depth_cm",
                }
            )


def profile_soil(stats: list[dict], completeness: list[dict]) -> None:
    source = DATA_DIR / "soil" / "wr373144a3" / "wr373144a3.txt"
    rows = []
    with source.open(encoding="utf-8") as file:
        for line in file:
            parts = line.split()
            if len(parts) != 28 or parts[0] not in STATIONS:
                continue
            try:
                year = int(parts[1])
            except ValueError:
                continue
            row = {
                "station_id": parts[0],
                "station_name": STATIONS[parts[0]],
                "year": year,
            }
            for idx, depth in enumerate(SOIL_DEPTHS_CM):
                row[f"soil_temp_{depth}cm_degC"] = numeric_or_nan(parts[4 + idx * 2], {"999.9"})
            rows.append(row)
    df = pd.DataFrame(rows)
    soil_cols = [f"soil_temp_{depth}cm_degC" for depth in SOIL_DEPTHS_CM]
    for (station_id, station_name), part in df.groupby(["station_id", "station_name"]):
        start, end = str(part["year"].min()), str(part["year"].max())
        for col in soil_cols:
            stats.append(
                stats_row(
                    "data/soil/wr373144a3/wr373144a3.txt",
                    col,
                    part[col],
                    station_id=station_id,
                    station_name=station_name,
                    period_start=start,
                    period_end=end,
                    unit="degC",
                    notes="Raw WMO fixed-width daily export; profile by station and depth.",
                )
            )
        for year, yearly in part.groupby("year"):
            for col in soil_cols:
                valid = int(yearly[col].notna().sum())
                completeness.append(
                    {
                        "source_file": "data/soil/wr373144a3/wr373144a3.txt",
                        "dimension": "station_year_parameter",
                        "key": f"{station_id}:{year}:{col}",
                        "expected_count": expected_days(int(year)),
                        "actual_count": valid,
                        "completeness_ratio": valid / expected_days(int(year)),
                        "notes": f"{station_name}; raw daily {col}",
                    }
                )


def profile_hydro(stats: list[dict], completeness: list[dict]) -> None:
    for source in sorted((DATA_DIR / "hydro").glob("lena-*.csv")):
        post = source.stem.replace("lena-", "")
        df = pd.read_csv(source, sep=";")
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df["Value"] = pd.to_numeric(df["Value"], errors="coerce")
        start = str(int(df["Date"].dt.year.min()))
        end = str(int(df["Date"].dt.year.max()))
        stats.append(
            stats_row(
                f"data/hydro/{source.name}",
                "water_level_cm",
                df["Value"],
                station_name=post,
                period_start=start,
                period_end=end,
                unit="cm",
                notes="Daily Lena River gauge file; one CSV per post.",
            )
        )
        for year, yearly in df.groupby(df["Date"].dt.year):
            valid = int(yearly["Value"].notna().sum())
            completeness.append(
                {
                    "source_file": f"data/hydro/{source.name}",
                    "dimension": "post_year_parameter",
                    "key": f"{post}:{int(year)}:water_level_cm",
                    "expected_count": expected_days(int(year)),
                    "actual_count": valid,
                    "completeness_ratio": valid / expected_days(int(year)),
                    "notes": "Daily Lena River gauge values.",
                }
            )


def profile_sts(stats: list[dict], completeness: list[dict]) -> None:
    source = DATA_DIR / "СТС.csv"
    df = pd.read_csv(source)
    year_cols = [col for col in df.columns if col.isdigit()]
    numeric_years = df[year_cols].apply(pd.to_numeric, errors="coerce")
    for year in year_cols:
        stats.append(
            stats_row(
                "data/СТС.csv",
                f"ALT_{year}",
                numeric_years[year],
                period_start=year,
                period_end=year,
                unit="cm",
                notes="Annual active-layer / seasonal thaw depth values across sites.",
            )
        )
    for idx, row in df.iterrows():
        site = row.get("Site Code", f"row_{idx}")
        actual = int(pd.to_numeric(row[year_cols], errors="coerce").notna().sum())
        completeness.append(
            {
                "source_file": "data/СТС.csv",
                "dimension": "site_year_columns",
                "key": site,
                "expected_count": len(year_cols),
                "actual_count": actual,
                "completeness_ratio": actual / len(year_cols),
                "notes": f"row_index={idx}",
            }
        )


def profile_mchs(stats: list[dict], completeness: list[dict]) -> None:
    for filename in ["mchs_events.csv", "mchs_events_lena_bank.csv"]:
        source = DATA_DIR / filename
        df = pd.read_csv(source)
        df["date_start"] = pd.to_datetime(df["date_start"], errors="coerce")
        df["date_end"] = pd.to_datetime(df["date_end"], errors="coerce")
        df["duration_days"] = (df["date_end"] - df["date_start"]).dt.days + 1
        df["damage_rub"] = pd.to_numeric(df["damage_rub"], errors="coerce")
        start = str(int(df["date_start"].dt.year.min()))
        end = str(int(df["date_start"].dt.year.max()))
        stats.append(
            stats_row(
                f"data/{filename}",
                "event_duration_days",
                df["duration_days"],
                period_start=start,
                period_end=end,
                unit="days",
                notes="Incident-level emergency archive.",
            )
        )
        stats.append(
            stats_row(
                f"data/{filename}",
                "damage_rub",
                df["damage_rub"],
                period_start=start,
                period_end=end,
                unit="rub",
                notes="Incident-level emergency archive; many records have no damage estimate.",
            )
        )
        for year, yearly in df.groupby(df["date_start"].dt.year):
            completeness.append(
                {
                    "source_file": f"data/{filename}",
                    "dimension": "event_year_count",
                    "key": int(year),
                    "expected_count": "",
                    "actual_count": int(len(yearly)),
                    "completeness_ratio": "",
                    "notes": "Count-only event coverage; no normative expected_count.",
                }
            )


def write_source_catalog() -> None:
    rows = [
        {
            "source_group": "air",
            "source_path": "data/air/wr373144a2/wr373144a2.txt",
            "file_format": "txt fixed-width",
            "primary_time_grain": "daily",
            "geographic_scope": "WMO stations 24266, 24343, 24688, 24944, 24959, 30230",
            "expected_period": "1882-2025; analytical window 2008-2023",
            "key_parameters": "mean air temperature, precipitation",
            "units": "degC; mm",
            "notes": "Raw Roshydromet/WMO export; station-level profiles in value_stats_raw.csv",
        },
        {
            "source_group": "snow",
            "source_path": "data/snow/wr373144a5/wr373144a5.txt",
            "file_format": "txt fixed-width",
            "primary_time_grain": "daily",
            "geographic_scope": "WMO stations 24266, 24343, 24688, 24944, 24959, 30230",
            "expected_period": "1882-2025; analytical window 2008-2023",
            "key_parameters": "snow depth",
            "units": "cm",
            "notes": "Raw Roshydromet/WMO export; winter features use October-April season",
        },
        {
            "source_group": "soil",
            "source_path": "data/soil/wr373144a3/wr373144a3.txt",
            "file_format": "txt fixed-width",
            "primary_time_grain": "daily",
            "geographic_scope": "WMO stations 24266, 24343, 24688, 24944, 24959, 30230",
            "expected_period": "1963-2024",
            "key_parameters": "soil temperature by depths 2-320 cm",
            "units": "degC",
            "notes": "Raw Roshydromet/WMO export; depth-level profiles in value_stats_raw.csv",
        },
        {
            "source_group": "hydro",
            "source_path": "data/hydro/lena-*.csv",
            "file_format": "csv semicolon-separated",
            "primary_time_grain": "daily",
            "geographic_scope": "Lena River gauges: Kirensk, Vitim, Lensk, Olekminsk, Pokrovsk, Yakutsk, Tabaga, Sangar, Zhigansk",
            "expected_period": "varies by gauge; analytical window 2008-2023",
            "key_parameters": "water level",
            "units": "cm",
            "notes": "One file per gauge; annual/spring features are derived into data_tables",
        },
        {
            "source_group": "sts",
            "source_path": "data/СТС.csv",
            "file_format": "csv",
            "primary_time_grain": "annual",
            "geographic_scope": "permafrost active-layer sites",
            "expected_period": "1990-2025; observed non-null values mainly 1992-2025",
            "key_parameters": "active-layer / seasonal thaw depth",
            "units": "cm",
            "notes": "Wide table with year columns; nonnumeric inactive values are treated as missing in profiles",
        },
        {
            "source_group": "mchs",
            "source_path": "data/mchs_events.csv",
            "file_format": "csv",
            "primary_time_grain": "event-based",
            "geographic_scope": "Republic of Sakha (Yakutia)",
            "expected_period": "1991-2024",
            "key_parameters": "emergency type, dates, location, season, damage",
            "units": "mixed",
            "notes": "Incident-level event archive",
        },
        {
            "source_group": "mchs",
            "source_path": "data/mchs_events_lena_bank.csv",
            "file_format": "csv",
            "primary_time_grain": "event-based",
            "geographic_scope": "Lena river bank zone",
            "expected_period": "2008-2023",
            "key_parameters": "emergency type, dates, location, season, damage",
            "units": "mixed",
            "notes": "Incident-level subset for Lena bank analysis",
        },
    ]
    pd.DataFrame(rows).to_csv(PROFILE_DIR / "source_catalog.csv", index=False, encoding="utf-8")


def main() -> None:
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    stats: list[dict] = []
    completeness: list[dict] = []

    profile_air(stats, completeness)
    profile_snow(stats, completeness)
    profile_soil(stats, completeness)
    profile_hydro(stats, completeness)
    profile_sts(stats, completeness)
    profile_mchs(stats, completeness)
    write_source_catalog()

    pd.DataFrame(stats).to_csv(PROFILE_DIR / "value_stats_raw.csv", index=False, encoding="utf-8")
    pd.DataFrame(completeness).to_csv(PROFILE_DIR / "completeness_report.csv", index=False, encoding="utf-8")

    print(f"Wrote {len(stats)} value-stat rows to {PROFILE_DIR / 'value_stats_raw.csv'}")
    print(f"Wrote {len(completeness)} completeness rows to {PROFILE_DIR / 'completeness_report.csv'}")
    print(f"Wrote source catalog to {PROFILE_DIR / 'source_catalog.csv'}")


if __name__ == "__main__":
    main()
