"""Descarga los recorridos de Ecobici 2022-2025 (Buenos Aires Data, CC BY 2.5 AR) a datos/crudos/.

Son unos 700 MB en total. El servidor rechaza clientes sin agente de navegador, por eso se envía uno.
Cada archivo se baja a un temporal y solo se renombra si llegó completo (tamaño igual al anunciado).
Al final escribe datos/procesados/manifiesto_descarga.json con fecha, tamaño y huella SHA-256 de cada ZIP.

Uso: python src/descargar_datos.py            (descarga lo que falte y rehace el manifiesto)
     python src/descargar_datos.py --manifiesto (solo rehace el manifiesto de los ZIP ya presentes)
"""
import hashlib
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

import requests

if __package__:
    from .config import ANIOS, DATOS_CRUDOS, DATOS_PROCESADOS, URL_RECORRIDOS
else:
    from config import ANIOS, DATOS_CRUDOS, DATOS_PROCESADOS, URL_RECORRIDOS

AGENTE = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
PLAZO_TOTAL_S = 3600  # una hora como máximo por archivo


def ruta_zip(anio):
    return DATOS_CRUDOS / f"recorridos-realizados-{anio}.zip"


def huellas_conocidas():
    """Huellas SHA-256 del manifiesto anterior, si existe (para reutilizar solo archivos verificados)."""
    ruta = DATOS_PROCESADOS / "manifiesto_descarga.json"
    if not ruta.exists():
        return {}
    return {a["archivo"]: a["sha256"] for a in json.loads(ruta.read_text(encoding="utf-8"))["archivos"]}


def bajar(anio, conocidas):
    destino = ruta_zip(anio)
    if destino.exists() and conocidas.get(destino.name) == huella(destino):
        return f"{anio}: ya estaba y su huella coincide con el manifiesto"
    url = URL_RECORRIDOS.format(anio=anio)
    temporal = destino.with_suffix(".zip.parcial")
    try:
        with requests.get(url, headers={"User-Agent": AGENTE}, stream=True, timeout=(30, 120)) as r:
            r.raise_for_status()
            esperado = int(r.headers.get("Content-Length", 0))
            inicio = time.monotonic()
            with open(temporal, "wb") as f:
                for bloque in r.iter_content(chunk_size=1 << 20):
                    if time.monotonic() - inicio > PLAZO_TOTAL_S:
                        raise TimeoutError(f"{anio}: la descarga superó {PLAZO_TOTAL_S} s")
                    f.write(bloque)
        if esperado and temporal.stat().st_size != esperado:
            raise IOError(f"{anio}: descarga incompleta")
        temporal.replace(destino)
    finally:
        temporal.unlink(missing_ok=True)
    return f"{anio}: {destino.stat().st_size:,} bytes"


def huella(ruta):
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        while bloque := f.read(1 << 20):
            h.update(bloque)
    return h.hexdigest()


def manifiesto():
    archivos = []
    for anio in ANIOS:
        ruta = ruta_zip(anio)
        estado = ruta.stat()
        archivos.append({
            "anio": anio,
            "archivo": ruta.name,
            "url": URL_RECORRIDOS.format(anio=anio),
            "bytes": estado.st_size,
            "sha256": huella(ruta),
            "modificado_local_utc": datetime.fromtimestamp(estado.st_mtime, timezone.utc).isoformat(timespec="seconds"),
        })
    datos = {"fuente": "Buenos Aires Data, Bicicletas públicas, Recorridos realizados (CC BY 2.5 AR)",
             "generado_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
             "archivos": archivos}
    DATOS_PROCESADOS.mkdir(parents=True, exist_ok=True)
    (DATOS_PROCESADOS / "manifiesto_descarga.json").write_text(
        json.dumps(datos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return datos


if __name__ == "__main__":
    DATOS_CRUDOS.mkdir(parents=True, exist_ok=True)
    if "--manifiesto" not in sys.argv:
        conocidas = huellas_conocidas()
        with ThreadPoolExecutor(max_workers=len(ANIOS)) as ex:
            for linea in ex.map(lambda a: bajar(a, conocidas), ANIOS):
                print(linea)
    for a in manifiesto()["archivos"]:
        print(a["archivo"], a["bytes"], a["sha256"][:16])
