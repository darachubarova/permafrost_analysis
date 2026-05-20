#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Decision Support System (DSS) CLI for Permafrost degradation and Hydrological risks in Yakutia.
Bilingual Russian/English interactive wizard for public authorities and EMERCOM.
"""

import os
import sys
import argparse
import pandas as pd
import numpy as np
from datetime import datetime

# Adjust paths to import permafrost_model
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from permafrost_model import (
    StefanClassicModel,
    StefanHybridModel,
    EmpiricalRegressionModel,
    SoilThermalTrendModel,
    HydroPropagationModel,
    DecisionSupportSystem,
    PSRS_Scorer
)

# Set console encoding to UTF-8
if sys.platform.startswith('win'):
    import ctypes
    # Set output code page to UTF-8
    ctypes.windll.kernel32.SetConsoleOutputCP(65001)
    ctypes.windll.kernel32.SetConsoleCP(65001)
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stdin.reconfigure(encoding='utf-8')

# Paths setup
DATA_DIR = os.path.dirname(os.path.abspath(__file__))
SOIL_FILE = os.path.join(DATA_DIR, "soil", "wr373144a3", "wr373144a3.txt")
AIR_FILE = os.path.join(DATA_DIR, "air", "wr373144a2", "wr373144a2.txt")
SNOW_FILE = os.path.join(DATA_DIR, "snow", "wr373144a5", "wr373144a5.txt")
CTC_FILE = os.path.join(DATA_DIR, "СТС.csv")
HYDRO_DIR = os.path.join(DATA_DIR, "hydro")
MONTHLY_ANOMALIES_FILE = os.path.join(DATA_DIR, "monthly_anomalies_operational.csv")

# Terminal colors for wow-factor UI
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_RED = "\033[91m"
COLOR_BLUE = "\033[94m"
COLOR_CYAN = "\033[96m"
COLOR_MAGENTA = "\033[95m"
COLOR_BOLD = "\033[1m"
COLOR_RESET = "\033[0m"

def print_header(ru, en, color=COLOR_CYAN):
    border = "=" * 80
    print(f"\n{color}{border}")
    print(f"{COLOR_BOLD}{ru.center(80)}")
    print(f"{en.center(80)}{COLOR_RESET}")
    print(f"{color}{border}{COLOR_RESET}")

def print_subheader(ru, en, color=COLOR_BLUE):
    border = "-" * 60
    print(f"\n{color}{border}")
    print(f"{COLOR_BOLD}{ru}")
    print(f"{en}{COLOR_RESET}")
    print(f"{color}{border}{COLOR_RESET}")

class DataEngine:
    """
    Handles dynamic reading and feature extraction from the historical raw WMO files for Yakutsk (24959)
    """
    def __init__(self):
        self.cached_years = {}
        
    def load_historical_year(self, year):
        if year in self.cached_years:
            return self.cached_years[year]
            
        # Initialize default values
        data = {
            'year': year,
            'ddt': None,
            'ddf': None,
            'precip_summer': None,
            'h_snow': None,
            't320': None,
            'ros': 0,
            'alt_measured': None,
            'lensk_peak': None,
            'lensk_peak_date': None,
            'olek_peak': None,
            'olek_peak_date': None,
            'ykt_peak_measured': None,
            'ykt_peak_date_measured': None,
            'zhig_peak_measured': None,
            'zhig_peak_date_measured': None,
            'anomalies': []
        }
        
        # 1. Air & Precip parser
        if os.path.exists(AIR_FILE):
            try:
                # Read daily air temperature
                air_records = []
                with open(AIR_FILE, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.startswith('24959'): # Yakutsk
                            parts = line.strip().split()
                            if len(parts) >= 8:
                                # Sometimes parts length varies, let's parse using character indices
                                yr = int(line[6:10].strip())
                                month = int(line[11:13].strip())
                                day = int(line[14:16].strip())
                                
                                mean_t_str = line[27:32].strip()
                                mean_t = float(mean_t_str) if (mean_t_str and mean_t_str not in ['99.9', '999.9']) else np.nan
                                
                                precip_str = line[43:48].strip()
                                precip = float(precip_str) if (precip_str and precip_str not in ['99.9', '999.9']) else 0.0
                                
                                air_records.append({'year': yr, 'month': month, 'day': day, 'tmean': mean_t, 'precip': precip})
                                
                df_air = pd.DataFrame(air_records)
                
                # Extract DDT
                df_yr = df_air[df_air['year'] == year]
                if len(df_yr[df_yr['tmean'].notna()]) > 300:
                    data['ddt'] = float(df_yr[df_yr['tmean'] > 0]['tmean'].sum())
                    data['precip_summer'] = float(df_yr[(df_yr['month'] >= 5) & (df_yr['month'] <= 9)]['precip'].sum())
                    
                # Extract DDF (winter season Oct of prev year to Apr of current year)
                df_prev = df_air[df_air['year'] == year - 1]
                winter_t_prev = df_prev[df_prev['month'] >= 10]['tmean'].values
                winter_t_curr = df_yr[df_yr['month'] <= 4]['tmean'].values
                winter_temps = np.concatenate([winter_t_prev, winter_t_curr])
                winter_temps = winter_temps[~np.isnan(winter_temps)]
                if len(winter_temps) > 150:
                    data['ddf'] = float(np.abs(winter_temps[winter_temps < 0]).sum())
                    
                # Extract ROS (winter thaw days in Nov-Mar of winter season)
                winter_t_prev_w = df_prev[df_prev['month'].isin([11, 12])]['tmean'].values
                winter_t_curr_w = df_yr[df_yr['month'].isin([1, 2, 3])]['tmean'].values
                winter_w_temps = np.concatenate([winter_t_prev_w, winter_t_curr_w])
                winter_w_temps = winter_w_temps[~np.isnan(winter_w_temps)]
                data['ros'] = int(np.sum(winter_w_temps > 0))
            except Exception as e:
                pass
                
        # 2. Snow depth parser
        if os.path.exists(SNOW_FILE):
            try:
                snow_records = []
                with open(SNOW_FILE, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.startswith('24959'): # Yakutsk
                            yr = int(line[6:10].strip())
                            month = int(line[11:13].strip())
                            
                            height_str = line[17:21].strip()
                            height = float(height_str) if (height_str and height_str != '9999') else 0.0
                            snow_records.append({'year': yr, 'month': month, 'snow_height': height})
                            
                df_snow = pd.DataFrame(snow_records)
                
                # Winter snow height (Nov of prev year to Mar of current year)
                df_snow_prev = df_snow[df_snow['year'] == year - 1]
                snow_prev = df_snow_prev[df_snow_prev['month'].isin([11, 12])]['snow_height'].values
                snow_curr = df_snow[(df_snow['year'] == year) & (df_snow['month'].isin([1, 2, 3]))]['snow_height'].values
                snow_winter = np.concatenate([snow_prev, snow_curr])
                if len(snow_winter) > 0:
                    data['h_snow'] = float(np.max(snow_winter))
            except Exception as e:
                pass
                
        # 3. Soil temperature parser
        if os.path.exists(SOIL_FILE):
            try:
                soil_records = []
                with open(SOIL_FILE, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.startswith('24959'): # Yakutsk
                            parts = line.strip().split()
                            if len(parts) == 28:
                                yr = int(parts[1])
                                t320 = float(parts[26]) if parts[26] != '999.9' else np.nan
                                soil_records.append({'year': yr, 't320': t320})
                                
                df_soil = pd.DataFrame(soil_records)
                df_soil_yr = df_soil[(df_soil['year'] == year) & (df_soil['t320'].notna())]
                if len(df_soil_yr) > 200:
                    data['t320'] = float(df_soil_yr['t320'].mean())
            except Exception as e:
                pass
                
        # 4. Measured ALT from CTC.csv
        if os.path.exists(CTC_FILE):
            try:
                ctc_df = pd.read_csv(CTC_FILE, encoding='utf-8')
                r42_row = ctc_df[ctc_df['Site Code'] == 'R42'].iloc[0]
                year_str = str(year)
                if year_str in ctc_df.columns:
                    val = r42_row[year_str]
                    if pd.notna(val) and val != 'inactive':
                        data['alt_measured'] = float(val)
            except Exception as e:
                pass
                
        # 5. Hydro peak parser
        if os.path.exists(HYDRO_DIR):
            try:
                def extract_peak(filename):
                    filepath = os.path.join(HYDRO_DIR, filename)
                    if not os.path.exists(filepath):
                        return None, None
                    df = pd.read_csv(filepath, sep=';', parse_dates=['Date'])
                    df.columns = ['Date', 'Value']
                    df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
                    df = df.dropna()
                    
                    df['Year'] = df['Date'].dt.year
                    df['Month'] = df['Date'].dt.month
                    
                    # Look in spring flood season (May and June)
                    df_spring = df[(df['Year'] == year) & (df['Month'].isin([5, 6]))]
                    if not df_spring.empty:
                        idx_max = df_spring['Value'].idxmax()
                        row_max = df_spring.loc[idx_max]
                        return float(row_max['Value']), row_max['Date']
                    return None, None
                    
                data['lensk_peak'], data['lensk_peak_date'] = extract_peak("lena-lensk.csv")
                data['olek_peak'], data['olek_peak_date'] = extract_peak("lena-olekminsk.csv")
                data['ykt_peak_measured'], data['ykt_peak_date_measured'] = extract_peak("lena-yakutsk.csv")
                data['zhig_peak_measured'], data['zhig_peak_date_measured'] = extract_peak("lena-zhigansk.csv")
            except Exception as e:
                pass
                
        # 6. Monthly anomalies parser
        if os.path.exists(MONTHLY_ANOMALIES_FILE):
            try:
                df_anom = pd.read_csv(MONTHLY_ANOMALIES_FILE)
                # Filter for Yakutsk (24959) and specified year
                df_ykt_anom = df_anom[(df_anom['station_id'] == 24959) & (df_anom['year'] == year)]
                for _, row in df_ykt_anom.iterrows():
                    data['anomalies'].append({
                        'month': int(row['month']),
                        'signals': row['signals'],
                        'risk_points': int(row['risk_points']),
                        'severity': row['severity']
                    })
            except Exception as e:
                pass
                
        self.cached_years[year] = data
        return data

def run_historical_diagnostics(data_engine, dss, solver_classic, solver_hybrid, solver_empirical, soil_warming, hydro_model):
    print_header(
        "ДИАГНОСТИКА ИСТОРИЧЕСКОГО ПЕРИОДА (2005 - 2024)",
        "HISTORICAL YEAR DIAGNOSTICS & RETROSPECTIVE RUN",
        COLOR_MAGENTA
    )
    
    # Prompt user for a year
    while True:
        try:
            year_input = input(f"{COLOR_BOLD}Введите интересующий год (2005-2024) [или нажмите Enter для 2020]: {COLOR_RESET}").strip()
            if not year_input:
                year = 2020
                break
            year = int(year_input)
            if 2005 <= year <= 2024:
                break
            else:
                print(f"{COLOR_RED}Пожалуйста, введите год в диапазоне 2005-2024.{COLOR_RESET}")
        except ValueError:
            print(f"{COLOR_RED}Некорректный ввод. Пожалуйста, введите число.{COLOR_RESET}")
            
    print(f"\n{COLOR_CYAN}>>> Загрузка и обработка метеорологических и геологических логов для г. Якутска за {year} год...{COLOR_RESET}")
    data = data_engine.load_historical_year(year)
    
    # Check if we have core temperature and soil features
    if data['ddt'] is None or data['h_snow'] is None:
        print(f"{COLOR_RED}Критическая ошибка: Исторические климатические данные для {year} года отсутствуют или повреждены.{COLOR_RESET}")
        return
        
    print(f"{COLOR_GREEN}Успешно распарсены климатические параметры г. Якутска:{COLOR_RESET}")
    print(f"  - Градусо-сутки таяния (DDT): {data['ddt']:.1f} °C-дней")
    print(f"  - Градусо-сутки замораживания (DDF): {data['ddf']:.1f} °C-дней" if data['ddf'] else "  - DDF: Нет данных")
    print(f"  - Высота снежного покрова (H_snow): {data['h_snow']:.1f} см")
    print(f"  - Осадки за летний период (P_summer): {data['precip_summer']:.1f} мм" if data['precip_summer'] else "  - Precip Summer: Нет данных")
    print(f"  - Число зимних оттепелей (ROS): {data['ros']} дней")
    
    # 1. Deep Soil Temperature Warming comparison
    print_subheader("1. Температурный режим вечной мерзлоты (глубина 3.2 м) | Permafrost Soil Temperature (3.2m)", COLOR_CYAN)
    t320_proj = soil_warming.predict(year)
    t320_actual = data['t320']
    
    print(f"  - Математический тренд (OLS): {t320_proj:.3f} °C")
    if t320_actual is not None:
        error_t = t320_actual - t320_proj
        print(f"  - Фактические измерения WMO:  {t320_actual:.3f} °C")
        print(f"  - Отклонение от векового тренда: {error_t:+.3f} °C (климатическая вариация)")
    else:
        print(f"  - Фактические измерения WMO:  [Нет данных для этого года]")
        
    # Projected Crossing Year
    fail_yr = soil_warming.get_failure_year()
    print(f"  - Расчётный год перехода через 0°C (деградация): {COLOR_RED}{COLOR_BOLD}{round(fail_yr)} г.{COLOR_RESET}")
    
    # 2. ALT Predictions Comparison
    print_subheader("2. Сезонное протаивание грунта (ALT R42) | Active Layer Thickness Evaluation", COLOR_CYAN)
    alt_classic = solver_classic.predict(data['ddt'])
    alt_hybrid = solver_hybrid.predict(data['ddt'], data['h_snow'])
    
    ddf_val = data['ddf'] if data['ddf'] is not None else 4100.0 # fallback mean
    p_sum_val = data['precip_summer'] if data['precip_summer'] is not None else 150.0 # fallback mean
    alt_empirical = solver_empirical.predict(data['ddt'], ddf_val, data['h_snow'], p_sum_val)
    
    print(f"  - Классическая модель Стефана: {alt_classic:.1f} см")
    print(f"  - Гибридная модель Стефана (со снегом): {alt_hybrid:.1f} см")
    print(f"  - Многофакторная эмпирическая регрессия: {COLOR_BOLD}{alt_empirical:.1f} см{COLOR_RESET}")
    
    if data['alt_measured'] is not None:
        print(f"  - {COLOR_GREEN}Фактические измерения CALM R42 (Туймада): {data['alt_measured']:.1f} см{COLOR_RESET}")
        print(f"  - Ошибка многофакторной регрессии: {data['alt_measured'] - alt_empirical:+.1f} см (MAE ~ 1.6 см)")
    else:
        print(f"  - Фактические измерения CALM R42: [Нет логов для этого года]")
        
    # 3. Decision Support System Evaluation (Permafrost Settlement Risk Score)
    print_subheader("3. Риск деградации мерзлоты и сценарные рекомендации МЧС | Permafrost Degradation Risk & DSS", COLOR_CYAN)
    
    # Use actual T320 if available, otherwise predicted
    t320_eval = t320_actual if t320_actual is not None else t320_proj
    alt_eval = data['alt_measured'] if data['alt_measured'] is not None else alt_empirical
    
    evaluation = dss.evaluate_year(alt_eval, t320_eval, data['h_snow'], data['ros'])
    
    score = evaluation['score']
    level = evaluation['level']
    color_code = COLOR_GREEN if evaluation['color'] == 'GREEN' else (COLOR_YELLOW if evaluation['color'] == 'YELLOW' else COLOR_RED)
    
    print(f"  - {COLOR_BOLD}Интегральный балл риска PSRS:{COLOR_RESET} {color_code}{COLOR_BOLD}{score:.2f} / 10.0{COLOR_RESET}")
    print(f"  - {COLOR_BOLD}Уровень угрозы (Threat Level):{COLOR_RESET} {color_code}{COLOR_BOLD}{level}{COLOR_RESET}")
    
    print(f"\n{color_code}{COLOR_BOLD}--- РЕКОМЕНДАЦИИ ДЛЯ ОРГАНОВ ВЛАСТИ И МЧС (RU) ---{COLOR_RESET}")
    for rec in evaluation['recommendations_ru']:
        print(f" {color_code}{rec}{COLOR_RESET}")
        
    print(f"\n{color_code}--- EMERCOM DECISION SUPPORT DIRECTIONS (EN) ---{COLOR_RESET}")
    for rec in evaluation['recommendations_en']:
        print(f" {color_code}{rec}{COLOR_RESET}")
        
    # 4. Hydrological Wave Propagation
    print_subheader("4. Прогноз волны весеннего половодья реки Лены | Hydrological Flood Wave Forecast", COLOR_CYAN)
    if data['lensk_peak'] is not None and data['olek_peak'] is not None:
        ykt_peak_proj = hydro_model.predict_peak_level(data['lensk_peak'], data['olek_peak'])
        warning_status, warning_msg_ru = hydro_model.evaluate_warning(ykt_peak_proj)
        
        print(f"  - Зафиксирован пик в г. Ленске:      {data['lensk_peak']:.0f} см ({data['lensk_peak_date'].strftime('%Y-%m-%d') if data['lensk_peak_date'] else 'Нет даты'})")
        print(f"  - Зафиксирован пик в г. Олёкминске:  {data['olek_peak']:.0f} см ({data['olek_peak_date'].strftime('%Y-%m-%d') if data['olek_peak_date'] else 'Нет даты'})")
        print(f"  - {COLOR_BOLD}Прогноз весеннего пика в г. Якутске:{COLOR_RESET} {COLOR_BOLD}{ykt_peak_proj:.1f} см{COLOR_RESET}")
        
        # Calculate projected dates
        if data['lensk_peak_date']:
            ykt_date_proj_lensk = hydro_model.predict_peak_date(data['lensk_peak_date'], origin='lensk')
            zhig_date_proj = hydro_model.predict_downstream_date(ykt_date_proj_lensk)
            print(f"  - Расчётная дата пика в г. Якутске (по Ленску):   {COLOR_BOLD}{ykt_date_proj_lensk.strftime('%Y-%m-%d')}{COLOR_RESET} (лаг: +4.4 дн.)")
            print(f"  - Расчётная дата пика в г. Жиганске (downstream):  {COLOR_BOLD}{zhig_date_proj.strftime('%Y-%m-%d')}{COLOR_RESET} (лаг: +3.8 дн. от Якутска)")
            
        if data['ykt_peak_measured'] is not None:
            err_level = data['ykt_peak_measured'] - ykt_peak_proj
            print(f"  - Фактический пик в г. Якутске:       {data['ykt_peak_measured']:.0f} см ({data['ykt_peak_date_measured'].strftime('%Y-%m-%d') if data['ykt_peak_date_measured'] else 'Нет даты'})")
            print(f"  - Погрешность уровня моделирования:   {err_level:+.1f} см")
            
        # Warning status color
        w_color = COLOR_GREEN if warning_status == 'NORMAL' else (COLOR_YELLOW if warning_status == 'WARNING' else COLOR_RED)
        print(f"  - {COLOR_BOLD}Статус предупреждения МЧС:{COLOR_RESET} {w_color}{COLOR_BOLD}{warning_status}{COLOR_RESET}")
        print(f"    {w_color}{warning_msg_ru}{COLOR_RESET}")
    else:
        print(f"  - Недостаточно исторических гидрологических логов в верховьях реки Лены для {year} года.")
        
    # 5. Extreme Anomalous Events extracted
    if data['anomalies']:
        print_subheader("5. Выявленные экстремальные месячные аномалии | Registered Monthly Anomalies (Yakutsk)", COLOR_MAGENTA)
        for anom in data['anomalies']:
            month_name_ru = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"][anom['month'] - 1]
            sev_color = COLOR_RED if anom['severity'] == 'экстремальная' else COLOR_YELLOW
            print(f"  - {COLOR_BOLD}{month_name_ru}:{COLOR_RESET} {anom['signals']}")
            print(f"    Баллы риска: {COLOR_BOLD}{anom['risk_points']}{COLOR_RESET} | Тяжесть аномалии: {sev_color}{COLOR_BOLD}{anom['severity']}{COLOR_RESET}")

def run_predictive_scenarios(dss, solver_classic, solver_hybrid, solver_empirical, soil_warming, hydro_model):
    print_header(
        "ПРОГНОЗНОЕ СЦЕНАРНОЕ МОДЕЛИРОВАНИЕ КЛИМАТИЧЕСКИХ ИЗМЕНЕНИЙ",
        "PREDICTIVE SCENARIO MODELING & CLINICAL TARGET TESTING",
        COLOR_YELLOW
    )
    
    # 1. Target Year Input
    while True:
        try:
            year_input = input(f"{COLOR_BOLD}Введите целевой год моделирования (2025-2070) [или нажмите Enter для 2035]: {COLOR_RESET}").strip()
            if not year_input:
                year = 2035
                break
            year = int(year_input)
            if 2025 <= year <= 2070:
                break
            else:
                print(f"{COLOR_RED}Пожалуйста, укажите год в диапазоне 2025 - 2070.{COLOR_RESET}")
        except ValueError:
            print(f"{COLOR_RED}Некорректный ввод. Укажите год числом.{COLOR_RESET}")
            
    # Calculate baseline projection trend parameters
    t320_base = soil_warming.predict(year)
    
    # 2. Climate Anomaly Input
    print(f"\n{COLOR_CYAN}Задайте климатический сценарий относительно исторической нормы:{COLOR_RESET}")
    
    # Temperature anomaly
    while True:
        try:
            temp_anom_str = input(f" - Аномалия летних температур (°C, например, +1.5 или +3.0) [Enter для авто-тренда]: ").strip()
            if not temp_anom_str:
                # Deduce warming anomaly based on linear trend
                # Historically baseline is around 2010s (~1900 DDT). In 2035 trend indicates more warming
                temp_anomaly = 0.0215 * (year - 2024)
                print(f"   (Авто-расчет температурного тренда: {temp_anomaly:+.2f} °C к 2024 году)")
                break
            temp_anomaly = float(temp_anom_str)
            break
        except ValueError:
            print(f"{COLOR_RED}Некорректное значение. Пожалуйста, введите вещественное число.{COLOR_RESET}")
            
    # Snow height anomaly
    while True:
        try:
            snow_pct_str = input(f" - Изменение толщины зимнего снега в % (например, +20 или -10) [Enter для нормы 0%]: ").strip()
            if not snow_pct_str:
                snow_pct = 0.0
                break
            snow_pct = float(snow_pct_str)
            break
        except ValueError:
            print(f"{COLOR_RED}Некорректное значение. Введите процент отклонения.{COLOR_RESET}")
            
    # Rain-on-Snow increase
    while True:
        try:
            ros_days_str = input(f" - Число дней с зимними оттепелями и жидкими осадками (ROS) (0-10) [Enter для нормы 1 день]: ").strip()
            if not ros_days_str:
                ros_days = 1
                break
            ros_days = int(ros_days_str)
            if 0 <= ros_days <= 20:
                break
            else:
                print(f"{COLOR_RED}Диапазон дней оттепелей от 0 до 20.{COLOR_RESET}")
        except ValueError:
            print(f"{COLOR_RED}Введите целое число дней.{COLOR_RESET}")
            
    # 3. River peaks
    print(f"\n{COLOR_CYAN}Задайте гидрологические условия для весеннего половодья реки Лены:{COLOR_RESET}")
    while True:
        try:
            lensk_str = input(f" - Пиковый уровень воды в г. Ленске в см (исторический средний ~560, опасный >800) [Enter для 620]: ").strip()
            if not lensk_str:
                lensk_peak = 620.0
                break
            lensk_peak = float(lensk_str)
            break
        except ValueError:
            print(f"{COLOR_RED}Введите уровень в см.{COLOR_RESET}")
            
    while True:
        try:
            olek_str = input(f" - Пиковый уровень воды в г. Олёкминске в см (средний ~720, опасный >1000) [Enter для 780]: ").strip()
            if not olek_str:
                olek_peak = 780.0
                break
            olek_peak = float(olek_str)
            break
        except ValueError:
            print(f"{COLOR_RED}Введите уровень в см.{COLOR_RESET}")
            
    # Calculate climate feature vectors for the scenarios
    # Mean baselines for DDT = 1950, DDF = 4120, H_snow = 35.4 cm, Precip_summer = 150 mm
    ddt_scenario = 1950.0 + (temp_anomaly * 150.0) # approx sensitivity
    ddf_scenario = 4120.0 - (temp_anomaly * 180.0)
    h_snow_scenario = 35.4 * (1.0 + (snow_pct / 100.0))
    precip_summer_scenario = 150.0 * (1.0 + (temp_anomaly * 0.05)) # warmer usually wetter in Yakutia
    
    # Deep soil temp projected under linear trend + winter snow insulation effect
    # Max snow depth increases deep soil temperature by ~0.008°C per cm
    snow_insulation_anomaly = 0.008 * (h_snow_scenario - 35.4)
    t320_scenario = t320_base + snow_insulation_anomaly + (temp_anomaly * 0.15)
    
    # 4. Compile predictions
    alt_classic = solver_classic.predict(ddt_scenario)
    alt_hybrid = solver_hybrid.predict(ddt_scenario, h_snow_scenario)
    alt_empirical = solver_empirical.predict(ddt_scenario, ddf_scenario, h_snow_scenario, precip_summer_scenario)
    
    # River peak forecast
    ykt_peak_proj = hydro_model.predict_peak_level(lensk_peak, olek_peak)
    warning_status, warning_msg_ru = hydro_model.evaluate_warning(ykt_peak_proj)
    
    # 5. Output beautiful bilingual scenario scorecard
    print_header(
        f"РЕЗУЛЬТАТЫ СЦЕНАРНОГО МОДЕЛИРОВАНИЯ ДЛЯ {year} ГОДА",
        f"SCENARIO CLIMATE PROJECTION SCORECARD FOR YEAR {year}",
        COLOR_GREEN
    )
    
    print(f"{COLOR_BOLD}Входные климатические параметры сценария:{COLOR_RESET}")
    print(f"  - Температура лета: {temp_anomaly:+.2f} °C к исторической норме")
    print(f"  - Высота снежного покрова: {h_snow_scenario:.1f} см ({snow_pct:+.1f}%)")
    print(f"  - Зимние жидкие осадки и оттепели (ROS): {ros_days} дней")
    print(f"  - Рассчитанные градусо-сутки таяния (DDT): {ddt_scenario:.1f} °C-дней")
    print(f"  - Рассчитанные градусо-сутки заморозки (DDF): {ddf_scenario:.1f} °C-дней")
    
    print_subheader("1. Деградация вечной мерзлоты и протаивание грунта (Tuymada R42)", COLOR_CYAN)
    print(f"  - Проекция среднегодовой температуры грунта T_3.2м: {COLOR_BOLD}{t320_scenario:.3f} °C{COLOR_RESET}")
    if t320_scenario >= 0.0:
        print(f"    {COLOR_RED}{COLOR_BOLD}[ВНИМАНИЕ / WARNING] Температура грунта выше 0°C! Полная потеря несущей способности свайных фундаментов.{COLOR_RESET}")
    else:
        years_to_failure = -t320_scenario / 0.0215
        print(f"    Грунт сохраняет мерзлое состояние. До критического оттаивания (~0°C) осталось около {years_to_failure:.1f} лет.")
        
    print(f"  - Сезонное протаивание (ALT) по разным моделям:")
    print(f"    * Классическая модель Стефана:         {alt_classic:.1f} см")
    print(f"    * Гибридная модель (изоляция снега):   {alt_hybrid:.1f} см")
    print(f"    * {COLOR_BOLD}Калиброванная многофакторная регрессия: {alt_empirical:.1f} см{COLOR_RESET}")
    
    # 6. DSS Risk evaluation
    print_subheader("2. Интегральный балл риска PSRS и рекомендации МЧС России", COLOR_CYAN)
    evaluation = dss.evaluate_year(alt_empirical, t320_scenario, h_snow_scenario, ros_days)
    score = evaluation['score']
    level = evaluation['level']
    color_code = COLOR_GREEN if evaluation['color'] == 'GREEN' else (COLOR_YELLOW if evaluation['color'] == 'YELLOW' else COLOR_RED)
    
    print(f"  - {COLOR_BOLD}Интегральный балл риска PSRS:{COLOR_RESET} {color_code}{COLOR_BOLD}{score:.2f} / 10.0{COLOR_RESET}")
    print(f"  - {COLOR_BOLD}Уровень угрозы деформации зданий:{COLOR_RESET} {color_code}{COLOR_BOLD}{level}{COLOR_RESET}")
    
    print(f"\n{color_code}{COLOR_BOLD}--- РЕКОМЕНДАЦИИ ПО ОРГАНИЗАЦИИ ИНЖЕНЕРНОЙ ЗАЩИТЫ (RU) ---{COLOR_RESET}")
    for rec in evaluation['recommendations_ru']:
        print(f" {color_code}{rec}{COLOR_RESET}")
        
    print(f"\n{color_code}--- EMERCOM EMERGENCY PLAN DIRECTIONS (EN) ---{COLOR_RESET}")
    for rec in evaluation['recommendations_en']:
        print(f" {color_code}{rec}{COLOR_RESET}")
        
    # 7. Hydrological Propagation
    print_subheader("3. Риски катастрофических наводнений в г. Якутске", COLOR_CYAN)
    print(f"  - Пик волны половодья в г. Якутске: {COLOR_BOLD}{ykt_peak_proj:.1f} см{COLOR_RESET}")
    
    w_color = COLOR_GREEN if warning_status == 'NORMAL' else (COLOR_YELLOW if warning_status == 'WARNING' else COLOR_RED)
    print(f"  - {COLOR_BOLD}Статус предупреждения МЧС:{COLOR_RESET} {w_color}{COLOR_BOLD}{warning_status}{COLOR_RESET}")
    print(f"    {w_color}{warning_msg_ru}{COLOR_RESET}")
    
    # Project travel dates based on today's simulated peak
    sim_base_date = datetime.now()
    ykt_date_proj = hydro_model.predict_peak_date(sim_base_date, origin='lensk')
    zhig_date_proj = hydro_model.predict_downstream_date(ykt_date_proj)
    print(f"  - Симуляция продвижения пика в пространстве-времени:")
    print(f"    * Выход пика из Ленска:  {sim_base_date.strftime('%Y-%m-%d')} (День t)")
    print(f"    * Прибытие в Якутск:     {ykt_date_proj.strftime('%Y-%m-%d')} (День t+4.4)")
    print(f"    * Прибытие в Жиганск:    {zhig_date_proj.strftime('%Y-%m-%d')} (День t+8.2)")

def show_equation_sheet():
    print_header(
        "СПРАВОЧНИК МАТЕМАТИЧЕСКИХ МОДЕЛЕЙ И ФОРМУЛ (ВКР)",
        "MATHEMATICAL EQUATIONS AND SCIENTIFIC MANUAL SHEET",
        COLOR_BLUE
    )
    
    print(f"""
{COLOR_BOLD}1. Модели глубины сезонного протаивания грунта (ALT):{COLOR_RESET}
  - {COLOR_BOLD}Классическая модель Стефана (Stefan Classic):{COLOR_RESET}
    ALT = E * sqrt(DDT)
    где E = 4.3448 (эмпирический калибровочный коэффициент для г. Якутска)
    
  - {COLOR_BOLD}Гибридная модель Стефана с термоизоляцией снега (Stefan Hybrid):{COLOR_RESET}
    ALT = E_base * sqrt(DDT) * (1 + beta * H_snow)
    где E_base = 4.1866, beta = 0.00155 (влияние 1 см снега увеличивает таяние летом на 0.155%)
    
  - {COLOR_BOLD}Многофакторное эмпирическое уравнение регрессии:{COLOR_RESET}
    ALT = 197.99 + 0.0096 * DDT - 0.0051 * DDF + 0.370 * H_snow - 0.0045 * P_summer
    Коэффициент детерминации R^2 = 0.523, средняя абсолютная ошибка MAE = 1.65 см.

{COLOR_BOLD}2. Модель векового тренда потепления мерзлых грунтов на глубине 3.2 м:{COLOR_RESET}
  - {COLOR_BOLD}Уравнение OLS-регрессии на основе логов с 1970 по 2024 гг.:{COLOR_RESET}
    T_320 = 0.02150 * Year - 43.44
    Скорость потепления: +0.215 °C за десятилетие (2.15 °C за век).
    Год пересечения нулевого порога (failure year): Year = 43.44 / 0.02150 ≈ 2030.5 г.

{COLOR_BOLD}3. Модель добегания пика половодья по руслу реки Лены:{COLOR_RESET}
  - {COLOR_BOLD}Уровенная регрессия для г. Якутска:{COLOR_RESET}
    H_yakutsk = -120.0 + 0.38 * H_lensk + 0.42 * H_olekminsk
  - {COLOR_BOLD}Средние временные лаги добегания волны (travel lags):{COLOR_RESET}
    * Ленск -> Якутск: 4.4 суток
    * Олёкминск -> Якутск: 3.9 суток
    * Якутск -> Жиганск: 3.8 суток

{COLOR_BOLD}4. Интегральный балл риска деградации оснований PSRS:{COLOR_RESET}
  - {COLOR_BOLD}Формула расчета:{COLOR_RESET}
    PSRS = clip(5.0 + 1.6 * (0.4 * Z_ALT + 0.3 * Z_T320 + 0.2 * Z_snow + 0.1 * Z_ros), 0.0, 10.0)
    где Z_param - Z-оценка отклонения параметра от его многолетней климатической нормы.
    Нормы для г. Якутска:
    * ALT: mean = 221.5 см, std = 12.8 см
    * T_320: mean = -0.58 °C, std = 0.32 °C
    * H_snow: mean = 35.4 см, std = 8.6 см
    * ROS (оттепели): mean = 1.6 дней, std = 1.1 дней
""")
    input(f"{COLOR_BOLD}Нажмите Enter для возврата в главное меню...{COLOR_RESET}")

def main():
    parser = argparse.ArgumentParser(description="Bilingual CLI Decision Support System for Permafrost and Hydro hazards.")
    parser.add_argument("--year", type=int, help="Run diagnostics for a specific historical year (e.g. 2020) and exit.")
    parser.add_argument("--interactive", action="store_true", help="Launch interactive terminal wizard (default).")
    args = parser.parse_args()
    
    # Initialize Core Engines
    data_engine = DataEngine()
    dss = DecisionSupportSystem()
    solver_classic = StefanClassicModel()
    solver_hybrid = StefanHybridModel()
    solver_empirical = EmpiricalRegressionModel()
    soil_warming = SoilThermalTrendModel()
    hydro_model = HydroPropagationModel()
    
    # Non-interactive CLI command run
    if args.year:
        if 2005 <= args.year <= 2024:
            # Re-implement print without menus for direct calls
            data = data_engine.load_historical_year(args.year)
            if data['ddt'] is None:
                print(f"Error: Historical data for year {args.year} is not available.")
                sys.exit(1)
            t320_proj = soil_warming.predict(args.year)
            t320_eval = data['t320'] if data['t320'] is not None else t320_proj
            alt_empirical = solver_empirical.predict(data['ddt'], data['ddf'] if data['ddf'] else 4100.0, data['h_snow'], data['precip_summer'] if data['precip_summer'] else 150.0)
            alt_eval = data['alt_measured'] if data['alt_measured'] is not None else alt_empirical
            
            evaluation = dss.evaluate_year(alt_eval, t320_eval, data['h_snow'], data['ros'])
            print(f"PSRS_SCORE={evaluation['score']:.2f}")
            print(f"SEVERITY_LEVEL={evaluation['level']}")
            print(f"COLOR={evaluation['color']}")
            print("RECOMMENDATIONS_RU:")
            for r in evaluation['recommendations_ru']:
                print(f" - {r}")
            print("RECOMMENDATIONS_EN:")
            for r in evaluation['recommendations_en']:
                print(f" - {r}")
            sys.exit(0)
        else:
            print(f"Error: Year must be in range [2005, 2024] for historical runs.")
            sys.exit(1)
            
    # Welcome banner with rich styling
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print_header(
            "ПАКЕТ ПОДДЕРЖКИ ПРИНЯТИЯ РЕШЕНИЙ (СППР) «ВЕЧНАЯ МЕРЗЛОТА & ЛЕНА»",
            "DECISION SUPPORT SYSTEM (DSS) 'PERMAFROST & LENA RIVER' FOR YAKUTIA",
            COLOR_BLUE
        )
        print(f"""
{COLOR_BOLD}Главное меню / Main Menu:{COLOR_RESET}
  {COLOR_CYAN}[1]{COLOR_RESET} Диагностика исторического года (2005 - 2024)
      Retrospective Historical Analysis & Emergency Audits
  {COLOR_CYAN}[2]{COLOR_RESET} Прогнозное сценарное моделирование климата (2025 - 2070)
      Future Predictive Scenarios & Emergency Simulations
  {COLOR_CYAN}[3]{COLOR_RESET} Математический аппарат и уравнения (ВКР)
      Mathematical Model Formulation & Equation Sheet
  {COLOR_CYAN}[4]{COLOR_RESET} Выход / Exit
        """)
        
        choice = input(f"{COLOR_BOLD}Выберите пункт меню (1-4): {COLOR_RESET}").strip()
        
        if choice == '1':
            run_historical_diagnostics(data_engine, dss, solver_classic, solver_hybrid, solver_empirical, soil_warming, hydro_model)
            print()
            input(f"{COLOR_BOLD}Нажмите Enter для продолжения...{COLOR_RESET}")
        elif choice == '2':
            run_predictive_scenarios(dss, solver_classic, solver_hybrid, solver_empirical, soil_warming, hydro_model)
            print()
            input(f"{COLOR_BOLD}Нажмите Enter для продолжения...{COLOR_RESET}")
        elif choice == '3':
            show_equation_sheet()
        elif choice == '4' or choice.lower() in ['exit', 'quit', 'q']:
            print(f"\n{COLOR_GREEN}Спасибо за использование СППР! Завершение работы.{COLOR_RESET}")
            break
        else:
            print(f"{COLOR_RED}Неверный пункт меню. Пожалуйста, попробуйте снова.{COLOR_RESET}")
            import time
            time.sleep(1.5)

if __name__ == '__main__':
    main()
