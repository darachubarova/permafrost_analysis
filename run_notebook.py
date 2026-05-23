"""Запуск permafrost_analysis.ipynb с рабочей директорией проекта."""
import sys
import asyncio
from pathlib import Path
import nbformat
from nbclient import NotebookClient

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

PROJECT_DIR = Path(__file__).parent.resolve()
NB_PATH = PROJECT_DIR / "NOPik" / "permafrost_analysis.ipynb"

print(f"Рабочая директория: {PROJECT_DIR}")
print(f"Ноутбук: {NB_PATH}")

with open(NB_PATH, encoding="utf-8") as f:
    nb = nbformat.read(f, as_version=4)

client = NotebookClient(
    nb,
    timeout=600,
    kernel_name="python3",
    allow_errors=True,
    resources={"metadata": {"path": str(PROJECT_DIR)}},
)

client.execute()

with open(NB_PATH, "w", encoding="utf-8") as f:
    nbformat.write(nb, f)

print("\nГотово. Ноутбук сохранён.")

errors = []
for i, cell in enumerate(nb.cells):
    if cell.cell_type != "code":
        continue
    for output in cell.get("outputs", []):
        if output.get("output_type") == "error":
            errors.append((i, output.get("ename"), output.get("evalue", "")[:120]))

if errors:
    print(f"\nЯчейки с ошибками ({len(errors)}):")
    for idx, ename, evalue in errors:
        print(f"  Ячейка {idx}: {ename}: {evalue}")
else:
    print("Ошибок не обнаружено.")
