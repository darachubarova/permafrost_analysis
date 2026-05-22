"""
Генерация таблиц описательных статистик весеннего периода по годам (2008–2023)
для 4 метеостанций: Киренск, Олёкминск, Якутск, Жиганск
"""
import pandas as pd
import numpy as np
import os

# Маппинг station_id -> название
STATIONS = {
    30230: "Киренск",
    24944: "Олёкминск",
    24959: "Якутск",
    24343: "Жиганск",
}

# === Парсинг суточных данных температуры и осадков ===
def parse_air_data(filepath):
    rows = []
    with open(filepath, "r", encoding="latin-1") as f:
        for line in f:
            parts = line.split()
            if len(parts) < 12:
                continue
            try:
                sid = int(parts[0])
                year = int(parts[1])
                month = int(parts[2])
                day = int(parts[3])
                # tmean — 8-й токен (индекс 7)
                tmean_str = parts[7]
                # precip — 11-й токен (индекс 11)
                precip_str = parts[11]
                tmean = float(tmean_str) if tmean_str not in ("9", "9.9", "99.9") else np.nan
                precip = float(precip_str) if precip_str not in ("9", "9.9") else 0.0
                rows.append((sid, year, month, day, tmean, precip))
            except (ValueError, IndexError):
                continue
    df = pd.DataFrame(rows, columns=["station_id", "year", "month", "day", "tmean", "precip"])
    return df

# === Парсинг суточных данных снега ===
def parse_snow_data(filepath):
    rows = []
    with open(filepath, "r", encoding="latin-1") as f:
        for line in f:
            parts = line.split()
            if len(parts) < 5:
                continue
            try:
                sid = int(parts[0])
                year = int(parts[1])
                month = int(parts[2])
                day = int(parts[3])
                snow_str = parts[4]
                snow = float(snow_str) if snow_str not in ("9999", "9998", "9997") else np.nan
                rows.append((sid, year, month, day, snow))
            except (ValueError, IndexError):
                continue
    df = pd.DataFrame(rows, columns=["station_id", "year", "month", "day", "snow_cm"])
    return df

BASE = os.path.dirname(os.path.abspath(__file__))
air_df = parse_air_data(os.path.join(BASE, "data/air/wr373144a2/wr373144a2.txt"))
snow_df = parse_snow_data(os.path.join(BASE, "data/snow/wr373144a5/wr373144a5.txt"))

# Фильтр: только целевые станции
air_df = air_df[air_df["station_id"].isin(STATIONS.keys())]
snow_df = snow_df[snow_df["station_id"].isin(STATIONS.keys())]

# Фильтр: весна (март=3, апрель=4, май=5) и период 2008–2023
spring_air = air_df[(air_df["month"].isin([3, 4, 5])) &
                    (air_df["year"] >= 2008) & (air_df["year"] <= 2023)]
spring_snow = snow_df[(snow_df["month"].isin([3, 4, 5])) &
                      (snow_df["year"] >= 2008) & (snow_df["year"] <= 2023)]

# Нормы температуры для каждой станции (медиана по всему периоду 2008-2023)
# используем для определения характера весны
station_norms = spring_air.groupby("station_id")["tmean"].median().to_dict()

def classify_spring(median_z):
    """Классификация характера весны по z-оценке медианы температуры."""
    if median_z >= 1.5:
        return "Аномально тёплая"
    elif median_z >= 0.5:
        return "Тёплая"
    elif median_z <= -1.5:
        return "Аномально холодная"
    elif median_z <= -0.5:
        return "Холодная"
    else:
        return "Норма"

# === Генерация таблиц по станциям ===
all_results = {}

for sid, name in STATIONS.items():
    s_air = spring_air[spring_air["station_id"] == sid]
    s_snow = spring_snow[spring_snow["station_id"] == sid]

    # Вычисляем среднее и std для z-оценки
    tmean_mean = s_air["tmean"].mean()
    tmean_std = s_air["tmean"].std()

    rows = []
    for year in range(2008, 2024):
        y_air = s_air[s_air["year"] == year]
        y_snow = s_snow[s_snow["year"] == year]

        t_med = round(y_air["tmean"].median(), 1) if not y_air.empty else None
        t_max = round(y_air["tmean"].max(), 1) if not y_air.empty else None
        precip_sum = round(y_air["precip"].sum(), 1) if not y_air.empty else None
        snow_max = round(y_snow["snow_cm"].max(), 0) if (not y_snow.empty and not y_snow["snow_cm"].isna().all()) else None

        # z-оценка медианы
        if t_med is not None and tmean_std > 0:
            z = (t_med - tmean_mean) / tmean_std
            spring_char = classify_spring(z)
        else:
            spring_char = "—"

        rows.append({
            "Период (Весна)": f"Весна {year} г.",
            "Среднесут. темп., °C (Медиана)": t_med if t_med is not None else "—",
            "Среднесут. темп., °C (Максимум)": t_max if t_max is not None else "—",
            "Сумма осадков за сезон, мм": precip_sum if precip_sum is not None else "—",
            "Высота снежного покрова, см (Макс)": int(snow_max) if snow_max is not None else "—",
            "Характер весны (отклонение)": spring_char,
        })

    df_out = pd.DataFrame(rows)
    all_results[name] = df_out
    df_out.to_csv(f"Spring_Stats_{name}.csv", index=False, sep=";", decimal=",")
    print(f"\n=== {name} ===")
    print(df_out.to_string(index=False))

print("\nГотово! Таблицы сохранены в Spring_Stats_*.csv")
