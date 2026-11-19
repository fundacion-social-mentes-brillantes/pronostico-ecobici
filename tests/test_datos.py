"""Comprobaciones de la lectura de los recorridos: columnas leídas, depuración, rutas con apóstrofo y ZIP anómalos."""
import zipfile

import duckdb
import pytest

from src import serie_horaria

CABECERA = ("Id_recorrido,duracion_recorrido,fecha_origen_recorrido,id_estacion_origen,"
            "fecha_destino_recorrido,id_estacion_destino,id_usuario,genero\n")


def test_solo_se_seleccionan_las_cinco_columnas_aunque_la_ruta_tenga_apostrofo(tmp_path):
    carpeta = tmp_path / "carpeta con 'apóstrofo'"
    carpeta.mkdir()
    csv = carpeta / "2024.csv"
    csv.write_text(CABECERA + "1BA,600,2024-01-01 10:00:00,5BA,2024-01-01 10:10:00,7BA,999BA,FEMALE\n",
                   encoding="utf-8")
    mapa, n_columnas = serie_horaria.mapa_columnas(duckdb.connect(), csv)
    assert n_columnas == 8
    assert set(mapa) == set(serie_horaria.COLUMNAS) and len(mapa) == 5
    assert "id_usuario" not in mapa.values() and "genero" not in mapa.values()


def test_la_depuracion_cuenta_cada_motivo_y_no_conserva_columnas_del_usuario(tmp_path):
    filas = [
        "1BA,600,2024-03-01 10:00:00,5BA,2024-03-01 10:10:00,7BA,u1,MALE",      # válido
        "2BA,30,2024-03-01 10:05:00,5BA,2024-03-01 10:05:30,5BA,u2,FEMALE",     # menos de 60 s, misma estación
        "3BA,0,2024-03-01 10:06:00,5BA,2024-03-01 10:06:00,8BA,u3,MALE",        # misma hora entre estaciones distintas
        "4BA,,2024-03-01 11:00:00,5BA,,7BA,u4,MALE",                            # sin hora de llegada
        "5BA,600,2024-03-01 12:00:00,5BA,2024-03-01 11:50:00,7BA,u5,MALE",      # llega antes de salir
        ",600,2024-03-01 13:00:00,5BA,2024-03-01 13:10:00,7BA,u6,MALE",         # sin identificador
        "7BA,600,2021-12-31 23:00:00,5BA,2021-12-31 23:10:00,7BA,u7,MALE",      # fuera del periodo
        "8BA,600,fecha mala,5BA,2024-03-01 13:10:00,7BA,u8,MALE",               # inicio inválido
    ]
    csv = tmp_path / "2024.csv"
    csv.write_text(CABECERA + "\n".join(filas) + "\n", encoding="utf-8")
    con = duckdb.connect()
    r = serie_horaria.depurar(con, csv, 2024)
    assert r["filas"] == 8 and r["filas_tras_depurar"] == 1
    assert r["llegada_ausente"] == 1 and r["llegada_antes_de_salida"] == 1 and r["identificador_ausente"] == 1
    assert r["menos_de_60_segundos"] == 2 and r["menos_de_60_segundos_misma_estacion"] == 1
    assert r["salida_y_llegada_iguales_entre_estaciones_distintas"] == 1
    assert r["inicio_invalido"] == 1 and r["inicio_fuera_de_periodo"] == 1
    columnas = [c[0] for c in con.execute("DESCRIBE limpio_2024").fetchall()]
    assert columnas == ["id", "inicio"]
    assert con.execute("SELECT id FROM limpio_2024").fetchall() == [("1BA",)]


def test_extraer_rechaza_un_zip_con_dos_csv(tmp_path, monkeypatch):
    monkeypatch.setattr(serie_horaria, "DATOS_CRUDOS", tmp_path)
    with zipfile.ZipFile(tmp_path / "recorridos-realizados-2030.zip", "w") as z:
        z.writestr("a.csv", CABECERA)
        z.writestr("b.csv", CABECERA)
    with pytest.raises(ValueError):
        serie_horaria.extraer(2030)


def test_extraer_usa_un_nombre_fijo_y_no_el_del_zip(tmp_path, monkeypatch):
    monkeypatch.setattr(serie_horaria, "DATOS_CRUDOS", tmp_path)
    with zipfile.ZipFile(tmp_path / "recorridos-realizados-2030.zip", "w") as z:
        z.writestr("../../fuera.csv", CABECERA)  # un nombre interno malicioso no debe usarse como ruta
    ruta = serie_horaria.extraer(2030)
    assert ruta.parent == tmp_path / "csv" and ruta.name.startswith("2030.") and ruta.suffix == ".csv"
    assert ruta.read_text(encoding="utf-8") == CABECERA
    assert not (tmp_path.parent / "fuera.csv").exists()
    assert not list((tmp_path / "csv").glob("*.parcial"))


class _MarcaFija:
    hex = "a" * 32


def test_extraer_no_borra_un_temporal_ajeno(tmp_path, monkeypatch):
    monkeypatch.setattr(serie_horaria, "DATOS_CRUDOS", tmp_path)
    monkeypatch.setattr(serie_horaria.uuid, "uuid4", lambda: _MarcaFija())
    with zipfile.ZipFile(tmp_path / "recorridos-realizados-2030.zip", "w") as z:
        z.writestr("a.csv", CABECERA)
    (tmp_path / "csv").mkdir()
    marca = f"{serie_horaria.os.getpid()}-{'a' * 12}"
    ajeno = tmp_path / "csv" / f"2030.csv.{marca}.parcial"
    ajeno.write_text("de otra ejecución", encoding="utf-8")
    with pytest.raises(FileExistsError):
        serie_horaria.extraer(2030)
    assert ajeno.read_text(encoding="utf-8") == "de otra ejecución"


def test_la_descarga_no_borra_un_temporal_ajeno(tmp_path, monkeypatch):
    from src import descargar_datos

    monkeypatch.setattr(descargar_datos, "DATOS_CRUDOS", tmp_path)
    monkeypatch.setattr(descargar_datos.uuid, "uuid4", lambda: _MarcaFija())
    monkeypatch.setattr(descargar_datos.requests, "get", lambda *a, **k: pytest.fail("no debía pedir nada"))
    destino = descargar_datos.ruta_zip(2030)
    ajeno = destino.with_suffix(f".zip.{descargar_datos.os.getpid()}-{'a' * 12}.parcial")
    ajeno.write_bytes(b"de otra ejecucion")
    with pytest.raises(FileExistsError):
        descargar_datos.bajar(2030, {})
    assert ajeno.read_bytes() == b"de otra ejecucion"
