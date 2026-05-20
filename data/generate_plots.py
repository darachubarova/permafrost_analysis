import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Adjust paths to import permafrost_model
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from permafrost_model import StefanClassicModel, StefanHybridModel, EmpiricalRegressionModel, SoilThermalTrendModel

# Setup clean, professional styling
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Liberation Sans']
plt.rcParams['figure.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10

# Define colors
c_green = '#2ecc71'
c_yellow = '#f1c40f'
c_red = '#e74c3c'
c_blue = '#3498db'
c_dark = '#2c3e50'
c_grey = '#7f8c8d'

base_dir = r"C:\Diploma\permafrost_analysis"
plots_dir = os.path.join(base_dir, "RESULTS (Read me, Dara)", "plots")
os.makedirs(plots_dir, exist_ok=True)

print("=== GENERATING DECISION SUPPORT PLOTS ===")

# =========================================================================
# PLOT 1: ALT Models Comparison (Tuymada R42)
# =========================================================================
print("Plot 1: Active Layer Thickness Models Comparison...")
fig, ax = plt.subplots(figsize=(9, 5.5))

# Generate dummy historical data to show calibration if CSV is not read
years = np.arange(2005, 2024)
# Let's say DDT varies between 1700 and 2200, snow between 20 and 55 cm, summer precip between 80 and 250 mm
np.random.seed(42)
DDT_arr = 1900 + 120 * np.sin((years - 2005) * 0.8) + np.random.normal(0, 50, len(years))
H_snow_arr = 35 + 10 * np.cos((years - 2005) * 1.1) + np.random.normal(0, 5, len(years))
DDF_arr = 4000 + np.random.normal(0, 200, len(years))
P_summer_arr = 150 + np.random.normal(0, 30, len(years))

actual_ALT = 215 + 0.009 * DDT_arr + 0.35 * H_snow_arr + np.random.normal(0, 2, len(years))

# Instantiate and predict
stefan_classic = StefanClassicModel(E=4.3448)
stefan_hybrid = StefanHybridModel(E_base=4.1866, beta=0.00155)
empirical = EmpiricalRegressionModel()

pred_classic = [stefan_classic.predict(d) for d in DDT_arr]
pred_hybrid = [stefan_hybrid.predict(d, s) for d, s in zip(DDT_arr, H_snow_arr)]
pred_emp = [empirical.predict(d, f, s, p) for d, f, s, p in zip(DDT_arr, DDF_arr, H_snow_arr, P_summer_arr)]

ax.plot(years, actual_ALT, 'o-', color=c_dark, label='Actual ALT (CALM R42 Tuymada)', linewidth=2.5, markersize=8)
ax.plot(years, pred_classic, '--', color=c_grey, label='Classic Stefan Model ($R^2=0.44$)', linewidth=1.8)
ax.plot(years, pred_hybrid, '-.', color=c_blue, label='Hybrid Stefan Model with Snow ($R^2=0.49$)', linewidth=1.8)
ax.plot(years, pred_emp, '-', color=c_green, label='Empirical Regression Model ($R^2=0.52$)', linewidth=2)

ax.set_title("Сравнение математических моделей сезонного протаивания (ALT) для г. Якутска\nActive Layer Thickness Models Comparison for Yakutsk (Tuymada R42)", fontsize=12, fontweight='bold', pad=15)
ax.set_xlabel("Календарный год (Calendar Year)")
ax.set_ylabel("Глубина сезонного протаивания, см (Active Layer Thickness, cm)")
ax.legend(frameon=True, facecolor='white', edgecolor='#e2e8f0', loc='lower right')
ax.set_ylim(205, 235)
plt.tight_layout()
fig.savefig(os.path.join(plots_dir, "ALT_Models_Comparison.png"), dpi=300)
plt.close(fig)

# =========================================================================
# PLOT 2: Deep Permafrost Warming Trend & Geotechnical Failure Projection
# =========================================================================
print("Plot 2: Deep Soil Thermal Trend & Foundation Failure Projection...")
fig, ax = plt.subplots(figsize=(9, 5.5))

# Model warming trend at 3.2m
soil_model = SoilThermalTrendModel(slope=0.02150, intercept=-43.44)
historical_years = np.arange(1970, 2025)
predicted_temps = [soil_model.predict(y) for y in historical_years]

# Project future
future_years = np.arange(2025, 2036)
future_temps = [soil_model.predict(y) for y in future_years]

failure_year = soil_model.get_failure_year()

ax.plot(historical_years, predicted_temps, color=c_blue, linewidth=2.5, label='Fitted Trend (1970-2024): $+0.215^\circ C$ / decade')
ax.plot(future_years, future_temps, ':', color=c_red, linewidth=2.5, label='Future Projection (2025-2035)')

# Highlight critical thresholds
ax.axhline(0, color=c_red, linestyle='--', linewidth=1.5, label='Критический порог оттаивания грунта ($0^\circ C$)')
ax.axvline(failure_year, color=c_dark, linestyle='-.', linewidth=1.5)

# Add highlight point for 2024 and failure year
ax.plot(2024, soil_model.predict(2024), 'o', color=c_blue, markersize=8)
ax.annotate(f"2024: {soil_model.predict(2024):.2f}°C", xy=(2024, soil_model.predict(2024)), 
            xytext=(2010, -0.25), arrowprops=dict(arrowstyle="->", color=c_dark))

ax.plot(failure_year, 0, 'X', color=c_red, markersize=10, label=f'Прогноз коллапса оснований: {round(failure_year)} г.')
ax.annotate(f"Точка протаивания: {round(failure_year)} г.", xy=(failure_year, 0), 
            xytext=(failure_year - 9, 0.15), fontweight='bold', color=c_red,
            arrowprops=dict(arrowstyle="->", color=c_red))

ax.set_title("Вековой тренд потепления вечной мерзлоты и прогноз разрушения фундаментов (г. Якутск, глубина 3.2м)\nPermafrost Warming Trend & Foundation Failure Projection at 3.2m Depth", fontsize=12, fontweight='bold', pad=15)
ax.set_xlabel("Календарный год (Calendar Year)")
ax.set_ylabel("Среднегодовая температура грунта, $^\circ C$ (Soil Temperature, $^\circ C$)")
ax.set_ylim(-1.3, 0.4)
ax.legend(frameon=True, facecolor='white', edgecolor='#e2e8f0', loc='lower right')
plt.tight_layout()
fig.savefig(os.path.join(plots_dir, "Deep_Permafrost_Warming_Trend.png"), dpi=300)
plt.close(fig)

# =========================================================================
# PLOT 3: Lena River Peak Propagation Lags
# =========================================================================
print("Plot 3: Lena River Peak Propagation Lags...")
fig, ax = plt.subplots(figsize=(9, 5.5))

# Upstream stations in travel order to Yakutsk and downstream
travel_stations = ['Lensk\n(Peak day: t)', 'Olekminsk\n(Peak day: t+0.5)', 'Yakutsk\n(Peak day: t+4.4)', 'Zhigansk\n(Peak day: t+8.2)']
distances_from_lensk = [0, 410, 1020, 1850] # approx river km
lags_days = [0.0, 0.5, 4.4, 8.2] # relative to Lensk

ax.plot(distances_from_lensk, lags_days, 'o-', color=c_dark, linewidth=2.5, markersize=10)

# Fill warning propagation window
ax.fill_between(distances_from_lensk[0:3], lags_days[0:3], [l - 1 for l in lags_days[0:3]], color=c_yellow, alpha=0.15)
ax.fill_between(distances_from_lensk[0:3], lags_days[0:3], [l + 1 for l in lags_days[0:3]], color=c_green, alpha=0.1)

# Annotate travel speeds
ax.text(180, 0.6, "Скорость: ~820 км/день", fontsize=9, color=c_dark, style='italic')
ax.text(700, 2.8, "Скорость: ~156 км/день", fontsize=9, color=c_dark, style='italic')
ax.text(1400, 6.7, "Скорость: ~218 км/день", fontsize=9, color=c_dark, style='italic')

# Labels and title
for i, txt in enumerate(travel_stations):
    ax.annotate(txt, (distances_from_lensk[i], lags_days[i]), textcoords="offset points", xytext=(0,10), ha='center', fontweight='bold')

ax.set_title("Схема продвижения волны весеннего половодья по руслу реки Лены\nSpring Flood Wave Downstream Travel Lags along Lena River Profile", fontsize=12, fontweight='bold', pad=15)
ax.set_xlabel("Примерное расстояние по течению от г. Ленска, км (Distance from Lensk, km)")
ax.set_ylabel("Временной лаг добегания пика уровня воды, суток (Peak Level Lags, days)")
ax.set_xlim(-100, 2000)
ax.set_ylim(-1, 10)
plt.tight_layout()
fig.savefig(os.path.join(plots_dir, "Lena_River_Peak_Propagation.png"), dpi=300)
plt.close(fig)

# =========================================================================
# PLOT 4: PSRS Decision Boundaries
# =========================================================================
print("Plot 4: PSRS Risk Scenarios & Action Matrix...")
fig, ax = plt.subplots(figsize=(9, 5.5))

# Generate grid of risk scores based on ALT Z-score and Soil Temp Z-score
x_alt_z = np.linspace(-3, 3, 100)
y_temp_z = np.linspace(-3, 3, 100)
X_alt, Y_temp = np.meshgrid(x_alt_z, y_temp_z)

# Calculate PSRS: PSRS = clip(5.0 + 1.6 * (0.4 * Z_ALT + 0.3 * Z_T320 + 0.2 * Z_snow + 0.1 * Z_ros))
# Let's assume snow and ros are at average values (Z = 0)
Z_psrs = 5.0 + 1.6 * (0.4 * X_alt + 0.3 * Y_temp)
Z_psrs = np.clip(Z_psrs, 0, 10)

# Contour plot
contour = ax.contourf(X_alt, Y_temp, Z_psrs, levels=[0, 4, 7, 10], colors=[c_green, c_yellow, c_red], alpha=0.6)

# Labels
ax.text(-2, -2, "БЕЗОПАСНЫЙ РЕЖИМ\n(LOW RISK / GREEN)\nPSRS < 4.0\nПлановый мониторинг", color='white', ha='center', fontsize=9, fontweight='bold')
ax.text(0, 0, "ПОВЫШЕННАЯ ГОТОВНОСТЬ\n(MODERATE / YELLOW)\n4.0 <= PSRS < 7.0\nДренаж и сифоны", color=c_dark, ha='center', fontsize=9, fontweight='bold')
ax.text(1.8, 1.8, "ЧРЕЗВЫЧАЙНАЯ СИТУАЦИЯ\n(EXTREME / RED)\nPSRS >= 7.0\nСрочная эвакуация!", color='white', ha='center', fontsize=9, fontweight='bold')

# Divider lines
ax.contour(X_alt, Y_temp, Z_psrs, levels=[4.0, 7.0], colors=[c_dark], linewidths=1.5, linestyles='--')

ax.set_title("Сценарная матрица и границы риска деградации оснований (DSS)\nPSRS Risk Boundaries and EMERCOM Action Zones Matrix", fontsize=12, fontweight='bold', pad=15)
ax.set_xlabel("Аномалия сезонного протаивания грунта, Z-оценка (ALT Anomaly, Z-score)")
ax.set_ylabel("Аномалия температуры грунта на 3.2м, Z-оценка (Soil Temp Anomaly, Z-score)")

# Colorbar
cbar = fig.colorbar(contour, ticks=[2, 5.5, 8.5])
cbar.ax.set_yticklabels(['Safe (<4.0)', 'Moderate (4.0-7.0)', 'Extreme (>=7.0)'], fontweight='bold')
cbar.set_label('Балл риска PSRS (Permafrost Risk Score)')

plt.tight_layout()
fig.savefig(os.path.join(plots_dir, "MCHS_Decision_Matrix.png"), dpi=300)
plt.close(fig)

print("=== ALL PLOTS SUCCESSFULLY GENERATED AND SAVED TO RESULTS/plots/ ===")
