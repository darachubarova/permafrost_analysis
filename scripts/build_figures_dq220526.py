#!/usr/bin/env python3
"""
Builds 10 figures for DQ-220526 remarks.

Input tables (real mode, default):
- data/daily_anomalies_operational.csv
- результаты/water_level_annual_features.csv
- результаты/water_level_peak_lags_yakutsk.csv
- результаты/water_chs_link_by_year.csv
- data/mchs_events_lena_bank.csv

Output figures:
- figures/fig_2_5_temp_anomalies_2008_2023.png
- figures/fig_2_6_precip_anomalies_2008_2023.png
- figures/fig_2_7_winter_thaw_days_2008_2023.png
- figures/fig_2_8_anomaly_severity_2008_2023.png
- figures/fig_2_9_hydropost_peak_levels_2008_2023.png
- figures/fig_2_10_peak_lag_by_hydropost_2008_2023.png
- figures/fig_2_11_hydro_extreme_share_vs_chs_2008_2023.png
- figures/fig_3_4_emergency_frequency_by_type.png
- figures/fig_3_5_emergency_monthly_distribution_2008_2023.png
- figures/fig_3_6_emergency_trend_2008_2023.png
"""

from __future__ import annotations

import argparse
import csv
import statistics
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

try:
    import matplotlib.pyplot as plt
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "Не найден matplotlib. Установите зависимость: pip install matplotlib"
    ) from exc

YEAR_START = 2008
YEAR_END = 2023
YEARS = list(range(YEAR_START, YEAR_END + 1))

# Типы ЧС, исключённые из анализа как нерелевантные для гидрологии и мерзлоты
EXCLUDED_TYPES: set[str] = {"Ветер"}

ANOMALY_COLORS = {
    "temp": "#d73027",
    "precip": "#4575b4",
    "thaw": "#fdae61",
    "moderate": "#74add1",
    "extreme": "#d73027",
}

HYDRO_POST_ORDER = [
    "Киренск",
    "Витим",
    "Ленск",
    "Олёкминск",
    "Покровск",
    "Якутск",
    "Табага",
    "Сангар",
    "Жиганск",
]


def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(
        description="Генерация 10 рисунков по замечаниям DQ-220526"
    )
    parser.add_argument("--demo", action="store_true", help="Демо-режим с синтетическими данными")
    parser.add_argument(
        "--daily-anomalies",
        default=str(root / "data" / "daily_anomalies_operational.csv"),
    )
    parser.add_argument(
        "--water-features",
        default=str(root / "результаты" / "water_level_annual_features.csv"),
    )
    parser.add_argument(
        "--peak-lags",
        default=str(root / "результаты" / "water_level_peak_lags_yakutsk.csv"),
    )
    parser.add_argument(
        "--water-chs",
        default=str(root / "результаты" / "water_chs_link_by_year.csv"),
    )
    parser.add_argument(
        "--mchs-events",
        default=str(root / "data" / "mchs_events_lena_bank.csv"),
    )
    parser.add_argument(
        "--output-dir",
        default=str(root / "figures"),
        help="Каталог для сохранения png",
    )
    return parser.parse_args()


def fail(msg: str) -> None:
    raise SystemExit(f"Ошибка: {msg}")


def require_file(path: Path) -> None:
    if not path.exists():
        fail(f"Входной файл не найден: {path}")
    if not path.is_file():
        fail(f"Ожидался файл, но получено: {path}")


def read_csv(path: Path, required_cols: list[str], delimiter: str = ",") -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh, delimiter=delimiter)
        if reader.fieldnames is None:
            fail(f"Пустой CSV или не прочитан заголовок: {path}")
        missing = [c for c in required_cols if c not in reader.fieldnames]
        if missing:
            fail(f"В {path} отсутствуют обязательные колонки: {', '.join(missing)}")
        return list(reader)


def in_period(year_raw: str) -> bool:
    try:
        year = int(float(year_raw))
    except (TypeError, ValueError):
        return False
    return YEAR_START <= year <= YEAR_END


def setup_style() -> None:
    plt.style.use("seaborn-v0_8-whitegrid")
    plt.rcParams.update(
        {
            "font.size": 10,
            "axes.titlesize": 11,
            "axes.labelsize": 10,
            "legend.fontsize": 9,
            "figure.titlesize": 12,
        }
    )


def save_fig(fig, output_dir: Path, name: str) -> None:
    out = output_dir / f"fig_{name}.png"
    fig.tight_layout()
    fig.savefig(out, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"Сохранено: {out}")


def build_real_data(args: argparse.Namespace) -> dict:
    daily_path = Path(args.daily_anomalies)
    water_features_path = Path(args.water_features)
    peak_lags_path = Path(args.peak_lags)
    water_chs_path = Path(args.water_chs)
    mchs_path = Path(args.mchs_events)

    for p in [daily_path, water_features_path, peak_lags_path, water_chs_path, mchs_path]:
        require_file(p)

    daily = read_csv(
        daily_path,
        ["year", "signals", "severity", "station_name"],
    )
    water_features = read_csv(
        water_features_path,
        ["post", "year", "spring_peak_cm"],
    )
    peak_lags = read_csv(
        peak_lags_path,
        [
            "year",
            "лаг пика Витим→Якутск, дней",
            "лаг пика Жиганск→Якутск, дней",
            "лаг пика Киренск→Якутск, дней",
            "лаг пика Ленск→Якутск, дней",
            "лаг пика Олёкминск→Якутск, дней",
            "лаг пика Покровск→Якутск, дней",
            "лаг пика Сангар→Якутск, дней",
            "лаг пика Табага→Якутск, дней",
        ],
    )
    water_chs = read_csv(
        water_chs_path,
        ["year", "hydro_extreme_share", "chs_count"],
    )
    mchs = read_csv(
        mchs_path,
        ["date_start", "type_chs"],
    )

    return {
        "daily": daily,
        "water_features": water_features,
        "peak_lags": peak_lags,
        "water_chs": water_chs,
        "mchs": mchs,
    }


def build_demo_data() -> dict:
    daily = []
    for y in YEARS:
        daily.extend(
            [
                {"year": str(y), "signals": "аномально тёплый день", "severity": "умеренная", "station_name": "Якутск"},
                {"year": str(y), "signals": "экстремальные суточные осадки", "severity": "экстремальная", "station_name": "Киренск"},
                {"year": str(y), "signals": "зимняя/весенняя оттепель", "severity": "умеренная", "station_name": "Олёкминск"},
            ]
        )

    water_features = []
    for pidx, post in enumerate(HYDRO_POST_ORDER):
        for y in YEARS:
            water_features.append({"post": post, "year": str(y), "spring_peak_cm": str(500 + pidx * 30 + (y - YEAR_START) * 2)})

    peak_lags = []
    for y in YEARS:
        peak_lags.append(
            {
                "year": str(y),
                "лаг пика Витим→Якутск, дней": "8",
                "лаг пика Жиганск→Якутск, дней": "-5",
                "лаг пика Киренск→Якутск, дней": "11",
                "лаг пика Ленск→Якутск, дней": "6",
                "лаг пика Олёкминск→Якутск, дней": "4",
                "лаг пика Покровск→Якутск, дней": "1",
                "лаг пика Сангар→Якутск, дней": "-3",
                "лаг пика Табага→Якутск, дней": "-1",
            }
        )

    water_chs = []
    for y in YEARS:
        water_chs.append(
            {
                "year": str(y),
                "hydro_extreme_share": str(0.2 + ((y - YEAR_START) % 5) * 0.1),
                "chs_count": str((y - YEAR_START) % 3),
            }
        )

    mchs = []
    for y in YEARS:
        mchs.append({"date_start": f"{y}-05-15", "type_chs": "Затор"})
        if y % 2 == 0:
            mchs.append({"date_start": f"{y}-06-20", "type_chs": "Половодье"})

    return {
        "daily": daily,
        "water_features": water_features,
        "peak_lags": peak_lags,
        "water_chs": water_chs,
        "mchs": mchs,
    }


def fig_temp_anomalies(daily: list[dict[str, str]], output_dir: Path) -> None:
    counts = Counter()
    for row in daily:
        if in_period(row.get("year", "")) and "аномально тёплый" in row.get("signals", "").lower():
            counts[int(float(row["year"]))] += 1
    values = [counts.get(y, 0) for y in YEARS]
    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.bar(YEARS, values, color=ANOMALY_COLORS["temp"])
    ax.set_title("Рис. 2.5: Аномально тёплые дни по годам")
    ax.set_xlabel("Год")
    ax.set_ylabel("Количество дней")
    ax.set_xticks(YEARS[::2])
    save_fig(fig, output_dir, "2_5_temp_anomalies_2008_2023")


def fig_precip_anomalies(daily: list[dict[str, str]], output_dir: Path) -> None:
    counts = Counter()
    for row in daily:
        if in_period(row.get("year", "")) and "осадки" in row.get("signals", "").lower():
            counts[int(float(row["year"]))] += 1
    values = [counts.get(y, 0) for y in YEARS]
    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.bar(YEARS, values, color=ANOMALY_COLORS["precip"])
    ax.set_title("Рис. 2.6: Дни с экстремальными осадками по годам")
    ax.set_xlabel("Год")
    ax.set_ylabel("Количество дней")
    ax.set_xticks(YEARS[::2])
    save_fig(fig, output_dir, "2_6_precip_anomalies_2008_2023")


def fig_thaw_days(daily: list[dict[str, str]], output_dir: Path) -> None:
    counts = Counter()
    for row in daily:
        if in_period(row.get("year", "")) and "оттепель" in row.get("signals", "").lower():
            counts[int(float(row["year"]))] += 1
    values = [counts.get(y, 0) for y in YEARS]
    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.bar(YEARS, values, color=ANOMALY_COLORS["thaw"])
    ax.set_title("Рис. 2.7: Зимние/весенние оттепели по годам")
    ax.set_xlabel("Год")
    ax.set_ylabel("Количество дней")
    ax.set_xticks(YEARS[::2])
    save_fig(fig, output_dir, "2_7_winter_thaw_days_2008_2023")


def fig_severity(daily: list[dict[str, str]], output_dir: Path) -> None:
    moderate = Counter()
    extreme = Counter()
    for row in daily:
        if not in_period(row.get("year", "")):
            continue
        year = int(float(row["year"]))
        sev = row.get("severity", "").strip().lower()
        if sev == "умеренная":
            moderate[year] += 1
        elif sev == "экстремальная":
            extreme[year] += 1
    mod_values = [moderate.get(y, 0) for y in YEARS]
    ext_values = [extreme.get(y, 0) for y in YEARS]
    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.bar(YEARS, mod_values, color=ANOMALY_COLORS["moderate"], label="Умеренная")
    ax.bar(YEARS, ext_values, bottom=mod_values, color=ANOMALY_COLORS["extreme"], label="Экстремальная")
    ax.set_title("Рис. 2.8: Структура аномалий по уровню серьёзности")
    ax.set_xlabel("Год")
    ax.set_ylabel("Количество дней")
    ax.set_xticks(YEARS[::2])
    ax.legend()
    save_fig(fig, output_dir, "2_8_anomaly_severity_2008_2023")


def fig_hydropost_peaks(water_features: list[dict[str, str]], output_dir: Path) -> None:
    accum = defaultdict(list)
    for row in water_features:
        if in_period(row.get("year", "")):
            post = row.get("post", "")
            try:
                val = float(row.get("spring_peak_cm", ""))
            except ValueError:
                continue
            accum[post].append(val)

    posts = []
    means = []
    for post in HYDRO_POST_ORDER:
        series = accum.get(post, [])
        if not series:
            continue
        posts.append(post)
        means.append(sum(series) / len(series))

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(posts, means, color="#457b9d")
    ax.set_title("Рис. 2.9: Средние весенние пики уровня воды по гидропостам")
    ax.set_xlabel("Гидропост (по течению Лены)")
    ax.set_ylabel("Уровень воды, см")
    ax.tick_params(axis="x", rotation=35)
    save_fig(fig, output_dir, "2_9_hydropost_peak_levels_2008_2023")


def fig_peak_lags(peak_lags: list[dict[str, str]], output_dir: Path) -> None:
    col_map = {
        "Киренск": "лаг пика Киренск→Якутск, дней",
        "Витим": "лаг пика Витим→Якутск, дней",
        "Ленск": "лаг пика Ленск→Якутск, дней",
        "Олёкминск": "лаг пика Олёкминск→Якутск, дней",
        "Покровск": "лаг пика Покровск→Якутск, дней",
        "Табага": "лаг пика Табага→Якутск, дней",
        "Сангар": "лаг пика Сангар→Якутск, дней",
        "Жиганск": "лаг пика Жиганск→Якутск, дней",
    }
    vals = defaultdict(list)
    for row in peak_lags:
        if not in_period(row.get("year", "")):
            continue
        for post, col in col_map.items():
            try:
                vals[post].append(float(row[col]))
            except ValueError:
                continue

    posts = []
    medians = []
    for post in HYDRO_POST_ORDER:
        if post == "Якутск":
            continue
        series = vals.get(post, [])
        if not series:
            continue
        posts.append(post)
        medians.append(statistics.median(series))

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(posts, medians, color="#1d3557")
    ax.axhline(0, color="black", linewidth=0.9)
    ax.set_title("Рис. 2.10: Медианный лаг пиков относительно гидропоста Якутск")
    ax.set_xlabel("Гидропост")
    ax.set_ylabel("Лаг, суток")
    ax.tick_params(axis="x", rotation=35)
    save_fig(fig, output_dir, "2_10_peak_lag_by_hydropost_2008_2023")


def fig_hydro_share_vs_chs(water_chs: list[dict[str, str]], output_dir: Path) -> None:
    years = []
    shares = []
    chs = []
    for row in water_chs:
        if not in_period(row.get("year", "")):
            continue
        years.append(int(float(row["year"])))
        shares.append(float(row["hydro_extreme_share"]))
        chs.append(float(row["chs_count"]))

    if not years:
        fail(
            "После фильтрации по периоду 2008–2023 не осталось данных в "
            "water_chs_link_by_year.csv для построения рис. 2.11"
        )

    data_points = sorted(zip(years, shares, chs), key=lambda x: x[0])
    years, shares, chs = zip(*data_points)

    fig, ax1 = plt.subplots(figsize=(10, 4.5))
    ax1.plot(years, shares, color="#2a9d8f", marker="o", label="Доля экстремумов")
    ax1.set_xlabel("Год")
    ax1.set_ylabel("Доля гидропостов с экстремумами", color="#2a9d8f")
    ax1.tick_params(axis="y", labelcolor="#2a9d8f")
    ax1.set_xticks(years[::2])

    ax2 = ax1.twinx()
    ax2.plot(years, chs, color="#e76f51", marker="s", label="Количество ЧС")
    ax2.set_ylabel("Количество ЧС", color="#e76f51")
    ax2.tick_params(axis="y", labelcolor="#e76f51")

    ax1.set_title("Рис. 2.11: Доля гидроэкстремумов и количество ЧС по годам")
    save_fig(fig, output_dir, "2_11_hydro_extreme_share_vs_chs_2008_2023")


def _parse_event_year_month(date_str: str) -> tuple[int, int] | None:
    try:
        d = date.fromisoformat(date_str)
    except ValueError:
        return None
    if YEAR_START <= d.year <= YEAR_END:
        return d.year, d.month
    return None


def fig_emergency_by_type(mchs: list[dict[str, str]], output_dir: Path) -> None:
    counter = Counter()
    for row in mchs:
        parsed = _parse_event_year_month(row.get("date_start", ""))
        if not parsed:
            continue
        t = row.get("type_chs", "Не указан")
        if t in EXCLUDED_TYPES:
            continue
        counter[t] += 1

    labels = [k for k, _ in counter.most_common()]
    values = [counter[k] for k in labels]

    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.bar(labels, values, color="#6a4c93")
    ax.set_title("Рис. 3.4: Частота ЧС по типам")
    ax.set_xlabel("Тип ЧС")
    ax.set_ylabel("Количество событий")
    ax.tick_params(axis="x", rotation=30)
    save_fig(fig, output_dir, "3_4_emergency_frequency_by_type")


def fig_emergency_monthly(mchs: list[dict[str, str]], output_dir: Path) -> None:
    counter = Counter({m: 0 for m in range(1, 13)})
    for row in mchs:
        parsed = _parse_event_year_month(row.get("date_start", ""))
        if not parsed:
            continue
        if row.get("type_chs", "") in EXCLUDED_TYPES:
            continue
        _, month = parsed
        counter[month] += 1

    months = list(range(1, 13))
    values = [counter[m] for m in months]

    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.bar(months, values, color="#ff9f1c")
    ax.set_title("Рис. 3.5: Помесячное распределение ЧС (2008–2023)")
    ax.set_xlabel("Месяц")
    ax.set_ylabel("Количество событий")
    ax.set_xticks(months)
    save_fig(fig, output_dir, "3_5_emergency_monthly_distribution_2008_2023")


def fig_emergency_trend(mchs: list[dict[str, str]], output_dir: Path) -> None:
    type_year_counts: dict[str, Counter] = defaultdict(lambda: Counter({y: 0 for y in YEARS}))
    for row in mchs:
        parsed = _parse_event_year_month(row.get("date_start", ""))
        if not parsed:
            continue
        t = row.get("type_chs", "Не указан")
        if t in EXCLUDED_TYPES:
            continue
        year, _ = parsed
        type_year_counts[t][year] += 1

    TYPE_COLORS = {
        "Затор": "#1d3557",
        "Половодье": "#457b9d",
        "Паводок": "#a8dadc",
        "Чрезвычайная пожароопасность": "#e76f51",
    }
    TYPE_LABELS = {
        "Чрезвычайная пожароопасность": "Пожароопасность",
    }

    fig, ax = plt.subplots(figsize=(10, 4.5))
    for t in sorted(type_year_counts):
        values = [type_year_counts[t].get(y, 0) for y in YEARS]
        color = TYPE_COLORS.get(t, "#888888")
        label = TYPE_LABELS.get(t, t)
        ax.plot(YEARS, values, marker="o", label=label, color=color)

    ax.set_title("Рис. 3.6: Годовая динамика количества ЧС по типам")
    ax.set_xlabel("Год")
    ax.set_ylabel("Количество событий")
    ax.set_xticks(YEARS[::2])
    ax.legend()
    save_fig(fig, output_dir, "3_6_emergency_trend_2008_2023")


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    setup_style()

    if args.demo:
        print("Запущен demo-режим: используются синтетические данные.")
        data = build_demo_data()
    else:
        data = build_real_data(args)

    fig_temp_anomalies(data["daily"], output_dir)
    fig_precip_anomalies(data["daily"], output_dir)
    fig_thaw_days(data["daily"], output_dir)
    fig_severity(data["daily"], output_dir)
    fig_hydropost_peaks(data["water_features"], output_dir)
    fig_peak_lags(data["peak_lags"], output_dir)
    fig_hydro_share_vs_chs(data["water_chs"], output_dir)
    fig_emergency_by_type(data["mchs"], output_dir)
    fig_emergency_monthly(data["mchs"], output_dir)
    fig_emergency_trend(data["mchs"], output_dir)

    print("Готово: сформировано 10 рисунков.")


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        sys.exit(1)
