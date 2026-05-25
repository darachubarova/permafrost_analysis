"""
Построение LC-кривых для ВКР.
Генерирует три рисунка:
  fig_2_12_lc_ddt_yakutsk.png   — LC-кривые DDT Якутск (2008–2023)
  fig_2_13_lc_hydro_peaks.png   — LC-кривые пиков уровней воды (4 поста)
  fig_2_14_lc_comparison.png    — Сравнение LC-кривых DDT vs уровень Якутска
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from pathlib import Path

HYDRO_DIR = Path(__file__).parent.parent / "data" / "hydro"
FIGURES_DIR = Path(__file__).parent.parent / "figures"
FIGURES_DIR.mkdir(exist_ok=True)

YEARS = list(range(2008, 2024))  # 2008–2023

# ── DDT Якутск из Таблицы 2.7 (°C·сутки, суммы положительных T за март–апрель) ──
DDT_YAKUTSK = {
    2008: 150, 2009: 180, 2010: 140, 2011: 220, 2012: 160,
    2013: 150, 2014: 280, 2015: 170, 2016: 200, 2017: 150,
    2018: 160, 2019: 140, 2020: 210, 2021: 120, 2022: 140, 2023: 170,
}

# ── Загрузка гидрологических пиков (март–июнь) ─────────────────────────────────
HYDRO_POSTS = {
    "Ленск":     "lena-lensk.csv",
    "Олёкминск": "lena-olekminsk.csv",
    "Якутск":    "lena-yakutsk.csv",
    "Жиганск":   "lena-zhigansk.csv",
}


def load_spring_peaks(filename: str) -> dict[int, float]:
    """Возвращает {год: максимальный уровень воды март–июнь}."""
    path = HYDRO_DIR / filename
    df = pd.read_csv(path, sep=";", parse_dates=["Date"])
    df["year"] = df["Date"].dt.year
    df["month"] = df["Date"].dt.month
    spring = df[df["month"].between(3, 6)]
    peaks = spring.groupby("year")["Value"].max()
    return {yr: peaks[yr] for yr in YEARS if yr in peaks.index}


# ── LC-алгоритм ─────────────────────────────────────────────────────────────────
def compute_lc(series: list[float]) -> tuple[np.ndarray, np.ndarray]:
    """
    Вычисляет базовую LC-кривую по алгоритму Алескерова–Голубенко (2003).

    Returns:
        t_norm : нормализованная позиция [0, 1]  (ось X)
        lc     : доля накопленного эффекта [0, 1] (ось Y)
    """
    x = np.array(series, dtype=float)
    x_min, x_max = x.min(), x.max()
    if x_max == x_min:
        v = np.ones_like(x)
    else:
        v = (x - x_min) / (x_max - x_min)

    # Сортируем по убыванию нормализованного значения (концентрация в хвосте)
    idx = np.argsort(v)[::-1]
    v_sorted = v[idx]

    total = v_sorted.sum()
    if total == 0:
        cumsum = np.zeros(len(v_sorted) + 1)
    else:
        cumsum = np.concatenate([[0], np.cumsum(v_sorted)]) / total

    n = len(v_sorted)
    t_norm = np.linspace(0, 1, n + 1)
    lc = 1 - cumsum  # доля оставшегося
    return t_norm, lc


def diagonal(n: int) -> tuple[np.ndarray, np.ndarray]:
    t = np.linspace(0, 1, n + 1)
    return t, 1 - t


# ── Рисунок 1: DDT Якутск ────────────────────────────────────────────────────────
def plot_lc_ddt():
    values = [DDT_YAKUTSK[yr] for yr in YEARS]
    t, lc = compute_lc(values)
    t_d, d = diagonal(len(values))

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Левый: LC + диагональ
    ax = axes[0]
    ax.plot(t_d, d, "k--", lw=1.2, label="Диагональ (равномерное\nраспределение)")
    ax.plot(t, lc, "b-o", ms=5, lw=2, label="LC-кривая DDT")
    ax.fill_between(t, d, lc, alpha=0.15, color="blue", label="Область концентрации")
    ax.set_xlabel("Доля периода наблюдений (0→1)", fontsize=11)
    ax.set_ylabel("Доля накопленного DDT", fontsize=11)
    ax.set_title("Рис. 2.12а. LC-кривая DDT\nЯкутск, 2008–2023", fontsize=11)
    ax.legend(fontsize=9)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.grid(alpha=0.4)

    # Правый: столбчатая диаграмма DDT
    ax2 = axes[1]
    colors = ["#c0392b" if v >= 200 else "#2980b9" if v <= 150 else "#27ae60"
              for v in values]
    ax2.bar(YEARS, values, color=colors, edgecolor="grey", lw=0.5)
    ax2.axhline(np.mean(values), color="k", ls="--", lw=1.2,
                label=f"Среднее = {np.mean(values):.0f} °C·сут")
    ax2.set_xlabel("Год", fontsize=11)
    ax2.set_ylabel("DDT (°C·сутки)", fontsize=11)
    ax2.set_title("Рис. 2.12б. Исходный ряд DDT\nЯкутск, 2008–2023", fontsize=11)
    ax2.legend(fontsize=9)
    ax2.set_xticks(YEARS); ax2.set_xticklabels(YEARS, rotation=45, ha="right")
    ax2.grid(axis="y", alpha=0.4)
    # Аннотируем пик 2014
    ax2.annotate("2014\n(аномалия)", xy=(2014, 280),
                 xytext=(2016, 265), arrowprops=dict(arrowstyle="->", color="red"),
                 fontsize=9, color="red")

    plt.tight_layout()
    out = FIGURES_DIR / "fig_2_12_lc_ddt_yakutsk.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {out}")


# ── Рисунок 2: LC-кривые пиков уровней воды ────────────────────────────────────
def plot_lc_hydro():
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    colors_map = {
        "Ленск": "#e74c3c",
        "Олёкминск": "#e67e22",
        "Якутск": "#2980b9",
        "Жиганск": "#27ae60",
    }

    # Левый: LC-кривые
    ax = axes[0]
    t_d, d = diagonal(len(YEARS))
    ax.plot(t_d, d, "k--", lw=1.2, label="Диагональ")

    peak_data = {}
    for post, fname in HYDRO_POSTS.items():
        peaks_dict = load_spring_peaks(fname)
        vals = [peaks_dict.get(yr, np.nan) for yr in YEARS]
        if np.sum(~np.isnan(vals)) < 5:
            continue
        peak_data[post] = vals
        vals_clean = [v for v in vals if not np.isnan(v)]
        t, lc = compute_lc(vals_clean)
        ax.plot(t, lc, "-o", ms=5, lw=2, color=colors_map[post], label=post)

    ax.set_xlabel("Доля периода наблюдений (0→1)", fontsize=11)
    ax.set_ylabel("Доля накопленного пика уровня", fontsize=11)
    ax.set_title("Рис. 2.13а. LC-кривые пиков уровней воды\n4 поста, 2008–2023", fontsize=11)
    ax.legend(fontsize=9)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.grid(alpha=0.4)

    # Правый: пики по годам
    ax2 = axes[1]
    for post, vals in peak_data.items():
        ax2.plot(YEARS, vals, "-o", ms=4, lw=1.8, color=colors_map[post], label=post)
    ax2.set_xlabel("Год", fontsize=11)
    ax2.set_ylabel("Пик уровня воды (см)", fontsize=11)
    ax2.set_title("Рис. 2.13б. Пики уровней воды (март–июнь)\n4 поста, 2008–2023", fontsize=11)
    ax2.legend(fontsize=9)
    ax2.set_xticks(YEARS); ax2.set_xticklabels(YEARS, rotation=45, ha="right")
    ax2.grid(alpha=0.4)

    plt.tight_layout()
    out = FIGURES_DIR / "fig_2_13_lc_hydro_peaks.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {out}")


# ── Рисунок 3: Сравнение DDT vs Уровень Якутска ──────────────────────────────────
def plot_lc_comparison():
    ddt_vals = [DDT_YAKUTSK[yr] for yr in YEARS]
    hydro_dict = load_spring_peaks("lena-yakutsk.csv")
    hydro_vals = [hydro_dict.get(yr, np.nan) for yr in YEARS]
    hydro_clean = [v for v in hydro_vals if not np.isnan(v)]

    t_ddt, lc_ddt = compute_lc(ddt_vals)
    t_hyd, lc_hyd = compute_lc(hydro_clean)
    t_d, d = diagonal(len(YEARS))

    fig, ax = plt.subplots(figsize=(7, 6))
    ax.plot(t_d, d, "k--", lw=1.2, label="Диагональ")
    ax.plot(t_ddt, lc_ddt, "r-o", ms=5, lw=2, label="DDT (климат. предиктор)")
    ax.plot(t_hyd, lc_hyd, "b-s", ms=5, lw=2, label="Пик уровня — Якутск (отклик)")

    # Зона «окна упреждения»
    t_common = np.linspace(0, 1, 200)
    lc_ddt_interp = np.interp(t_common, t_ddt, lc_ddt)
    lc_hyd_interp = np.interp(t_common, t_hyd, lc_hyd)
    ax.fill_between(t_common, lc_ddt_interp, lc_hyd_interp,
                    where=(lc_ddt_interp > lc_hyd_interp),
                    alpha=0.2, color="green", label="Зона операц. окна упреждения")

    ax.set_xlabel("Нормализованная позиция (ранг / n)", fontsize=12)
    ax.set_ylabel("Доля накопленного значения (LC)", fontsize=12)
    ax.set_title("Рис. 2.14. Сравнение LC-кривых:\nДДТ (предиктор) vs уровень воды Якутск (отклик)\n2008–2023", fontsize=11)
    ax.legend(fontsize=10)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.grid(alpha=0.4)

    plt.tight_layout()
    out = FIGURES_DIR / "fig_2_14_lc_comparison.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {out}")


if __name__ == "__main__":
    print("Building LC-curve figures…")
    plot_lc_ddt()
    plot_lc_hydro()
    plot_lc_comparison()
    print("Done.")
