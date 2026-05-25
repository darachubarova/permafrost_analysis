import nbformat as nbf
from textwrap import dedent

nb = nbf.v4.new_notebook()

cells = []

intro = dedent(r"""
# Анализ временных рядов методом LC-кривых

Этот ноутбук демонстрирует реализацию методики LC-кривых (Life Cycle Curves) для анализа временных рядов индекса деловой неопределённости или других экономических индикаторов.

**Что делает ноутбук:**
- загружает временной ряд (уровень индекса и, при наличии, индикатор фазы/роста),
- строит LC-кривые по описанной в статье схеме,
- визуализирует динамику исходного индекса и LC-кривых,
- позволяет сравнивать спецификации ex-ante и ex-post.

> Примечание: точные формулы можно адаптировать под конкретное определение LC-кривых в вашей задаче — здесь реализован типичный подход, при котором LC-кривая строится как зависимость нормированного уровня индекса от его нормированной динамики.
""")

cells.append(nbf.v4.new_markdown_cell(intro))

imports = dedent(r"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

plt.style.use('seaborn-v0_8-darkgrid')
""")

cells.append(nbf.v4.new_code_cell(imports))

load_data_md = dedent(r"""
## Загрузка и подготовка данных

Ожидается, что у вас есть CSV-файл со следующей структурой:

- `date` — дата (или квартал/период) в формате `YYYY-MM-DD` или любая строка, распознаваемая `pandas.to_datetime`,
- `value` — уровень индекса (например, ИДН),
- (опционально) `spec` — спецификация индекса (`ex_ante`, `ex_post` и т.п.) для одновременного анализа нескольких рядов.

При необходимости адаптируйте имена колонок в коде ниже.
""")

cells.append(nbf.v4.new_markdown_cell(load_data_md))

load_data_code = dedent(r"""
# Путь к файлу с данными
# Замените 'data.csv' на ваш файл
DATA_PATH = Path('data.csv')

# Чтение и базовая подготовка
raw = pd.read_csv(DATA_PATH)

# Преобразование даты
raw['date'] = pd.to_datetime(raw['date'])

# Если нет колонки 'spec', создадим одну фиктивную
if 'spec' not in raw.columns:
    raw['spec'] = 'single'

raw = raw.sort_values(['spec', 'date']).reset_index(drop=True)

raw.head()
""")

cells.append(nbf.v4.new_code_cell(load_data_code))

lc_function_md = dedent(r"""
## Функции для расчёта LC-кривых

Реализуем обобщённую функцию, которая по временному ряду рассчитывает:

- нормированный уровень индекса \( u_t \) (например, min-max нормировка в диапазон \([0,1]\)),
- нормированную динамику (рост/изменение) \( g_t \) (например, темп изменения или разность, также нормированную в \([0,1]\)),
- точки LC-кривой \( (u_t, g_t) \).

Вы можете модифицировать формулы нормировки и роста в соответствии с точным определением в вашей методике.
""")

cells.append(nbf.v4.new_markdown_cell(lc_function_md))

lc_function_code = dedent(r"""
def min_max_scale(series: pd.Series) -> pd.Series:
    """Min-max нормировка в [0, 1] с защитой от деления на ноль."""
    s_min = series.min()
    s_max = series.max()
    if np.isclose(s_max, s_min):
        return pd.Series(0.5, index=series.index)
    return (series - s_min) / (s_max - s_min)


def compute_lc_curve(df: pd.DataFrame,
                     value_col: str = 'value',
                     date_col: str = 'date',
                     growth_mode: str = 'diff') -> pd.DataFrame:
    """Рассчитать LC-кривую для одного временного ряда.

    Параметры
    ---------
    df : DataFrame с колонками даты и значений.
    value_col : имя колонки с исходным индексом.
    date_col : имя колонки с датой/периодом.
    growth_mode : способ вычисления динамики:
        - 'diff'  : простая разность value_t - value_{t-1}
        - 'pct'   : относительное изменение (value_t / value_{t-1} - 1)

    Возвращает
    ---------
    DataFrame с колонками:
        date, value, value_norm, growth, growth_norm
    """
    df = df.copy().sort_values(date_col)

    # Нормированный уровень индекса
    value = df[value_col].astype(float)
    value_norm = min_max_scale(value)

    # Вычисление роста
    if growth_mode == 'diff':
        growth = value.diff()
    elif growth_mode == 'pct':
        growth = value.pct_change()
    else:
        raise ValueError("growth_mode должен быть 'diff' или 'pct'")

    growth_norm = min_max_scale(growth.fillna(0.0))

    out = df[[date_col, value_col]].copy()
    out['value_norm'] = value_norm.values
    out['growth'] = growth.values
    out['growth_norm'] = growth_norm.values

    return out
""")

cells.append(nbf.v4.new_code_cell(lc_function_code))

viz_md = dedent(r"""
## Визуализация LC-кривых

Теперь построим несколько графиков:

1. Динамика исходного индекса во времени.
2. LC-кривая: рост против уровня \( (u_t, g_t) \) в нормированных координатах.
3. (Опционально) сравнение LC-кривых для разных спецификаций (ex-ante vs ex-post).
""")

cells.append(nbf.v4.new_markdown_cell(viz_md))

viz_code_single = dedent(r"""
# Пример построения LC-кривой для одной спецификации
spec = 'single'  # замените на 'ex_ante' или 'ex_post' при необходимости

subset = raw[raw['spec'] == spec].copy()
lc = compute_lc_curve(subset, value_col='value', date_col='date', growth_mode='diff')

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# 1. Динамика индекса
axes[0].plot(lc['date'], lc['value'], marker='o')
axes[0].set_title(f'Динамика индекса ({spec})')
axes[0].set_xlabel('Дата')
axes[0].set_ylabel('Значение индекса')

# 2. LC-кривая (нормированные значения)
sc = axes[1].scatter(lc['value_norm'], lc['growth_norm'], c=range(len(lc)), cmap='viridis')
axes[1].set_title(f'LC-кривая (norm) — {spec}')
axes[1].set_xlabel('Нормированный уровень индекса')
axes[1].set_ylabel('Нормированная динамика индекса')

cbar = fig.colorbar(sc, ax=axes[1])
cbar.set_label('Время (номер периода)')

plt.tight_layout()
plt.show()
""")

cells.append(nbf.v4.new_code_cell(viz_code_single))

viz_code_compare = dedent(r"""
# Сравнение LC-кривых для разных спецификаций (если есть колонка 'spec')

specs = raw['spec'].unique()

fig, ax = plt.subplots(1, 1, figsize=(7, 6))

for s in specs:
    subset = raw[raw['spec'] == s].copy()
    lc = compute_lc_curve(subset, value_col='value', date_col='date', growth_mode='diff')
    ax.plot(lc['value_norm'], lc['growth_norm'], marker='o', label=s)

ax.set_title('Сравнение LC-кривых по спецификациям')
ax.set_xlabel('Нормированный уровень индекса')
ax.set_ylabel('Нормированная динамика индекса')
ax.legend()

plt.tight_layout()
plt.show()
""")

cells.append(nbf.v4.new_code_cell(viz_code_compare))

extensions_md = dedent(r"""
## Возможные расширения

- Заменить min-max нормировку на z-оценки или другую схему, используемую в вашей задаче.
- Добавить раскраску точек по фазам делового цикла (например, кризис, восстановление, рост, замедление).
- Ввести сглаживание временного ряда (скользящее среднее, фильтры) перед расчётом LC-кривых.
- Реализовать классификацию фаз на основе положения точки в пространстве \( (u_t, g_t) \).
""")

cells.append(nbf.v4.new_markdown_cell(extensions_md))

nb['cells'] = cells

output_path = Path('output')
output_path.mkdir(exist_ok=True)

nb_path = output_path / 'lc_curves_analysis.ipynb'
with open(nb_path, 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

nb_path.as_posix()