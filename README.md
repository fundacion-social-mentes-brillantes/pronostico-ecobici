# Pronóstico de viajes horarios de Ecobici Buenos Aires con datos retrasados

Comparativa de cinco técnicas para pronosticar cuántos viajes de **Ecobici** (el sistema público de bicicletas de
Buenos Aires) se inician en cada hora, y de **cuánto empeora cada una cuando el último dato disponible tiene 1, 24
o 168 horas de antigüedad**. Datos reales: 11,9 millones de recorridos de 2022 a 2025.

**Página del proyecto:** https://fundacion-social-mentes-brillantes.github.io/pronostico-ecobici/ (el hallazgo con un gráfico interactivo, el método, los límites y la memoria
en PDF para descargar).

> **Qué es este repositorio.** Una prueba de capacidades de dos asistentes de IA, **Claude** (Anthropic) y
> **Codex** (OpenAI), encargada por la Fundación Social Mentes Brillantes: llevar de principio a fin un
> trabajo con la forma y la exigencia de un Trabajo Fin de Máster en Inteligencia Artificial (tipo «comparativa de
> soluciones»). **No es un trabajo presentado ante ninguna universidad.** El detalle de quién hizo qué está en el
> Anexo A de la memoria, y las instrucciones que recibió Codex, en `proceso_ia/`.

## Resultados

Error absoluto medio (MAE) en viajes por hora, sobre 4.244 horas de prueba (julio a diciembre de 2025; media de
374,7 viajes por hora):

| Método | Dato de hace 1 h | Dato de hace 24 h | Dato de hace 168 h |
|---|---|---|---|
| *Boosting* de árboles | **31,15** | **78,28** | **89,44** |
| Perceptrón multicapa | 33,34 | 80,75 | 89,61 |
| Regresión Ridge | 34,88 | 87,41 | 92,43 |
| Ingenuo semanal | 104,36 | 104,36 | 104,36 |
| Mediana de calendario | 111,71 | 111,71 | 111,71 |
| *Boosting* + clima observado (secundario) | 30,21 | 59,33 | 65,29 |

- **En este caso, la frescura del dato pesó más que el modelo.** Entre modelos competentes hubo un 10 % de
  diferencia. Con el dato de hace un día, el error de los modelos ajustados se multiplicó por cerca de 2,5.
  Entre las cinco alternativas principales, el *boosting* tuvo el menor MAE en los tres retrasos. Con 168 horas,
  el perceptrón quedó segundo, a 0,17 viajes por hora.
- La ventaja del *boosting* sobre la referencia ingenua fue del 70 %, el 25 % y el 14 % con datos de 1, 24 y 168 h,
  significativa en cada escenario (Diebold-Mariano con varianza de Newey-West y corrección de Holm; se mantiene con
  48, 168 y 336 rezagos).
- El clima casi no cambió el error con datos frescos (−3,0 %) y lo redujo mucho con datos atrasados (−24 % a −27 %).
  Ojo: se usó el clima observado (ERA5), que se publica después; no es lo que daría un pronóstico del tiempo.
- Hallazgo de datos: el archivo de 2024 trae 321.015 recorridos de menos de un minuto (frente a 0 en 2022 y 2023 y 8
  en 2025) y 3.379 sin hora de llegada; se filtraron con el mismo criterio en los cuatro años.

![Error por método y retraso](resultados/figuras/03_mae_por_metodo.png)

## Cómo está hecho

| Paso | Script | Qué hace |
|---|---|---|
| 1 | `src/descargar_datos.py` | Baja los recorridos de Ecobici 2022-2025 (Buenos Aires Data, CC BY 2.5 AR; ~700 MB) y guarda sus huellas SHA-256 |
| 2 | `src/serie_horaria.py` | Lee los CSV con SQL (DuckDB) sin seleccionar nunca las columnas del usuario; depura y arma la serie por hora |
| 3 | `src/descargar_clima.py` | Temperatura y lluvia por hora de Open-Meteo (ERA5, CC BY 4.0) |
| 4 | `src/feriados.py` | Feriados y días no laborables de Argentina 2022-2025, con las correcciones de cada año |
| 5 | `src/ejecutar_todo.py` | Variables por escenario, cinco modelos, validación, prueba, Diebold-Mariano, figuras, tablas, datos de la web (`src/exportar_web.py`) y registro de la ejecución (menos de un minuto) |
| 6 | `memoria/construir_docx.py`, `memoria/construir_pdf.py` y `memoria/construir_gdocs.py` | La memoria en Word (editable), en PDF (diseño editorial, con Edge o Chrome sin ventana) y para Google Docs (el diseño del PDF en un documento editable) a partir de los capítulos en Markdown |

Protocolo: entrenamiento 2022-2024, validación enero-junio de 2025 y prueba julio-diciembre de 2025, con un margen
de siete días entre bloques; los modelos se congelan antes de la prueba y todas las alternativas se evalúan en las
mismas horas. Las veinte pruebas automáticas (`tests/`) comprueban, entre otras cosas, que ninguna variable use datos
posteriores al corte de cada escenario; corren en GitHub Actions con cada cambio.

## Reproducir

Con Python 3.12 (en Linux o macOS, `.venv/bin/python`):

```
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
.venv/Scripts/python -m pytest -q
.venv/Scripts/python src/ejecutar_todo.py
```

Los datos procesados ya están en `datos/procesados/`. Para reconstruirlos desde los recorridos originales, después
de crear el entorno: `src/descargar_datos.py`, `src/serie_horaria.py`, `src/descargar_clima.py` y `src/feriados.py`,
en ese orden.

## Memoria y página web

- Memoria en PDF: `memoria/memoria.pdf` (también se descarga desde la página). En Word, editable:
  `memoria/memoria.docx`. Para Google Docs, con el diseño del PDF: `memoria/construir_gdocs.py` arma un .docx que,
  subido a Google Drive con conversión, queda como documento nativo de Google Docs. En Markdown, por capítulos, en
  `memoria/`.
- Página: carpeta `web/` (HTML, CSS y JavaScript sin librerías; gráficos SVG dibujados a mano). Se publica en
  GitHub Pages con `.github/workflows/pagina.yml`. Sus cifras salen de `web/datos.js`, que genera
  `src/exportar_web.py`; una prueba comprueba que coincidan con los resultados.
- Sistema de diseño común a la web, el PDF y las figuras: `DESIGN.md` (estilo «Ciudad de noche», escogido entre tres
  propuestas; letras Newsreader y Schibsted Grotesk, con licencia OFL, en `web/fuentes/` y `recursos/fuentes/`).
- Las cuatro ilustraciones de la página y la portada del PDF (`web/img/`, `memoria/portada.jpg`) las generó Codex con
  IA a partir de indicaciones de Claude; no son fotografías.

## Licencias

Código: MIT. Texto de la memoria: CC BY 4.0. Datos derivados: recorridos de Ecobici del Gobierno de la Ciudad de
Buenos Aires (CC BY 2.5 AR), depurados y agregados por hora; clima de Open-Meteo y Copernicus ERA5 (CC BY 4.0).
