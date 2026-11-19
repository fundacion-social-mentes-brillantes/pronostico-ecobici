"""Ejecuta el experimento, las figuras, las tablas de la memoria y los datos de la web, y deja un registro."""
import json
import os
import platform
from datetime import datetime, timezone
from importlib.metadata import version
from time import perf_counter

if __package__:
    from . import config
    from .experimento import ejecutar_experimento
    from .exportar_web import main as exportar_web
    from .graficos import generar_figuras
    from .tablas_memoria import main as generar_tablas
else:
    import config
    from experimento import ejecutar_experimento
    from exportar_web import main as exportar_web
    from graficos import generar_figuras
    from tablas_memoria import main as generar_tablas

LIBRERIAS = ["numpy", "pandas", "scikit-learn", "matplotlib", "duckdb", "threadpoolctl"]


def main():
    # Se borra el registro anterior: si algún paso falla, no queda un registro viejo junto a resultados nuevos.
    (config.RESULTADOS / "registro_ejecucion.json").unlink(missing_ok=True)
    tiempos = {}
    inicio_total = perf_counter()
    for nombre, paso in (("experimento", ejecutar_experimento), ("figuras", generar_figuras),
                         ("tablas_memoria", generar_tablas), ("web", exportar_web)):
        inicio = perf_counter()
        paso()
        tiempos[nombre] = round(perf_counter() - inicio, 2)
    tiempos["total"] = round(perf_counter() - inicio_total, 2)
    registro = {
        "fecha_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "tiempos_s": tiempos,
        "python": platform.python_version(),
        "sistema": platform.platform(),
        "procesador": platform.processor(),
        "nucleos_logicos": os.cpu_count(),
        "librerias": {n: version(n) for n in LIBRERIAS},
    }
    (config.RESULTADOS / "registro_ejecucion.json").write_text(
        json.dumps(registro, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Experimento, figuras, tablas y web completados en {tiempos['total']:.2f} s.")


if __name__ == "__main__":
    main()
