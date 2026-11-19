"""Descarga los recorridos de Ecobici 2022-2025 (Buenos Aires Data, CC BY 2.5 AR) a datos/crudos/.

Son unos 700 MB en total. El servidor rechaza clientes sin agente de navegador, por eso se envía uno.
Cada archivo se baja a un temporal y solo se renombra si llegó completo (tamaño igual al anunciado).
Al final escribe datos/procesados/manifiesto_descarga.json con fecha, tamaño y huella SHA-256 de cada ZIP.

Uso: python src/descargar_datos.py            (descarga lo que falte y rehace el manifiesto)
     python src/descargar_datos.py --manifiesto (solo rehace el manifiesto de los ZIP ya presentes)
"""
import hashlib
import json
import os
import sys
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

import requests

if __package__:
    from .config import ANIOS, DATOS_CRUDOS, DATOS_PROCESADOS, URL_RECORRIDOS
else:
    from config import ANIOS, DATOS_CRUDOS, DATOS_PROCESADOS, URL_RECORRIDOS

AGENTE = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
# Plazo total por archivo: una hora, contada desde antes de pedir el archivo. Se comprueba cada vez que llega un
# bloque (64 KB). Además, la conexión se corta si pasan 30 s sin poder conectarse o 120 s seguidos sin recibir
# ningún dato. Así, una descarga detenida se corta en 120 s; una que sigue avanzando, aunque sea muy despacio, se
# corta al llegar el primer bloque después de cumplida la hora.
PLAZO_TOTAL_S = 3600
BLOQUE = 64 * 1024


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
    # Proceso + marca aleatoria: único aunque el sistema reutilice el número de proceso.
    temporal = destino.with_suffix(f".zip.{os.getpid()}-{uuid.uuid4().hex[:12]}.parcial")
    inicio = time.monotonic()
    creado = False  # solo se borra el temporal si lo creó esta llamada
    try:
        with open(temporal, "xb") as f:  # "x": falla si el archivo ya existiera
            creado = True
            with requests.get(url, headers={"User-Agent": AGENTE}, stream=True, timeout=(30, 120)) as r:
                r.raise_for_status()
                esperado = int(r.headers.get("Content-Length", 0))
                for bloque in r.iter_content(chunk_size=BLOQUE):
                    if time.monotonic() - inicio > PLAZO_TOTAL_S:
                        raise TimeoutError(f"{anio}: la descarga superó {PLAZO_TOTAL_S} s")
                    f.write(bloque)
        if time.monotonic() - inicio > PLAZO_TOTAL_S:  # también si el final llegó tarde, sin un bloque más
            raise TimeoutError(f"{anio}: la descarga superó {PLAZO_TOTAL_S} s")
        if esperado and temporal.stat().st_size != esperado:
            raise IOError(f"{anio}: descarga incompleta")
        temporal.replace(destino)
    finally:
        if creado:
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
