# Anexo A. Declaración de uso de inteligencia artificial

Este trabajo es una **prueba de capacidades de dos asistentes de inteligencia artificial**, encargada por
una persona de la Fundación Social Mentes Brillantes que no es programadora, para comprobar hasta dónde pueden llevar por
sí solos un trabajo con la forma y la exigencia de un Trabajo Fin de Máster. **No es un Trabajo Fin de Estudios
presentado ante UNIR ni ante ninguna otra universidad**, y no debe presentarse como tal.

Participaron (Anthropic, 2026; OpenAI, 2026):

- **Claude** (Anthropic, modelo Claude Opus 5.5), que dirigió el trabajo: definió el tema y el diseño experimental,
  buscó y comprobó la bibliografía, descargó y depuró los datos, escribió los scripts de preparación y de tablas,
  revisó, corrigió y ejecutó el código de los modelos, redactó los capítulos 1, 4, 5, 6, 7 y 8, el resumen y los
  anexos, revisó todo el documento, diseñó y construyó la página web del proyecto y este PDF, y escribió el comando
  que pronostica una hora concreta (`src/pronosticar.py`).
- **Codex** (OpenAI, modelos GPT-6.2 Sol, GPT-6.1 Terra y GPT-6 Luna), que propuso temas candidatos, revisó la propuesta como
  segundo lector, programó los modelos, el protocolo de evaluación, las pruebas automáticas y las figuras, redactó
  los primeros borradores de los capítulos 2 y 3 y los ajustó, y revisó el proyecto completo (memoria y código) en
  una revisión final de 30 puntos. Después revisó la página web, el PDF y las figuras, generó con IA las cuatro
  ilustraciones de la página web (una de ellas es también la portada de este documento; no son fotografías) y
  criticó el diseño a partir de capturas.

La revisión final de Codex llevó a corregir varias cifras, a contar por separado 3.379 recorridos sin hora de
llegada, a reforzar la seguridad y la robustez del código (ruta del archivo como parámetro de la consulta SQL,
descargas a un archivo temporal con huellas SHA-256, validación de la rejilla del clima y de las entradas del
contraste) y a moderar varias afirmaciones que el experimento no permite sostener. En la primera repetición tras
las correcciones de robustez, la serie, el clima, las predicciones y los contrastes salieron idénticos; solo
cambió una cifra descriptiva, los días secos, por un ajuste de redondeo. Después, la revisión detectó que faltaba el feriado del
2 de septiembre de 2022. Se corrigió el calendario y se repitió el experimento. Todas las cifras de la memoria
proceden de esa última ejecución (`resultados/`). Las limitaciones de diseño se recogen en la sección 7.4.

En total Codex recibió más de veinte encargos de revisión, programación y redacción, más los de las ilustraciones y
las críticas de diseño; cada tanda de arreglos se repitió hasta que respondió «SIN ERRORES PENDIENTES». Las
instrucciones exactas que recibió Codex y sus respuestas están en la carpeta `proceso_ia/` del repositorio, incluidas
las de las ilustraciones y las críticas de diseño (`20-ilustraciones-y-criticas-codex.md`).
Todas las referencias bibliográficas se comprobaron una por una en Crossref, arXiv o la página oficial de la
fuente; ninguna se tomó de la memoria de un modelo sin verificar.

# Anexo B. Repositorio y reproducción

El repositorio público (https://github.com/fundacion-social-mentes-brillantes/pronostico-ecobici) contiene:

| Carpeta o archivo | Contenido |
|---|---|
| `src/config.py` | Rutas, fechas de las particiones, escenarios y semilla |
| `src/descargar_datos.py` | Descarga de los recorridos de Ecobici 2022-2025 (unos 700 MB) y manifiesto con huellas |
| `src/serie_horaria.py` | Lectura con SQL (DuckDB), depuración y serie horaria con control de cobertura |
| `src/descargar_clima.py` | Temperatura y precipitación horarias de Open-Meteo (ERA5) |
| `src/feriados.py` | Calendario de feriados y días no laborables 2022-2025 |
| `src/variables.py`, `src/modelos.py`, `src/estadistica.py`, `src/experimento.py` | Variables por escenario, alternativas, métricas y contraste, y protocolo |
| `src/graficos.py`, `src/tablas_memoria.py`, `src/exportar_web.py`, `src/ejecutar_todo.py` | Figuras, tablas complementarias, datos de la página web y ejecución completa con registro |
| `src/pronosticar.py` | Pronóstico de una hora concreta con los modelos del estudio |
| `tests/` | Treinta y dos pruebas automáticas |
| `datos/procesados/` | Serie horaria, clima, feriados y manifiesto de la descarga |
| `resultados/` | Métricas, hiperparámetros, contrastes, predicciones, tablas, registro de ejecución y figuras |
| `memoria/` | Esta memoria, en Markdown por capítulos, en Word, en PDF y para Google Docs (`construir_docx.py`, `construir_pdf.py` y `construir_gdocs.py`) |
| `web/` | Página del proyecto, publicada en https://fundacion-social-mentes-brillantes.github.io/pronostico-ecobici/ |
| `proceso_ia/` | Encargos y respuestas de Codex |

Pasos, con Python 3.12 (en Linux o macOS, `.venv/bin/python` en lugar de `.venv/Scripts/python`):

```
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
.venv/Scripts/python -m pytest -q
.venv/Scripts/python src/ejecutar_todo.py
```

Eso repite el experimento con los datos procesados que ya trae el repositorio. Para reconstruir antes esos datos
desde los recorridos originales, después de crear el entorno y antes de las pruebas:

```
.venv/Scripts/python src/descargar_datos.py
.venv/Scripts/python src/serie_horaria.py
.venv/Scripts/python src/descargar_clima.py
.venv/Scripts/python src/feriados.py
```

Para pedirle a los modelos del estudio el pronóstico de una hora concreta:

```
.venv/Scripts/python src/pronosticar.py "2025-12-24 18:00"
```

El comando muestra lo que pronostica cada método con el dato de hace 1 hora, 1 día y 1 semana y, si esa hora ya
tiene dato, el valor real. Usa los mismos modelos del experimento, ajustados con los datos de 2022 a junio de 2025,
así que en las horas de prueba da las mismas cifras que guardó el experimento (salvo diferencias de redondeo de
menos de una billonésima de viaje). Después del último dato publicado,
cada escenario llega solo hasta donde alcanza su retraso: una hora, un día o una semana más allá.

# Anexo C. Días que marcaba la regla de bajo volumen (descartada)

La regla marcaba como dudosos los días con menos del 25 % de la mediana del mismo día de la semana en las cuatro
semanas anteriores y posteriores (sección 4.3), usando el total diario de viajes incluso en los días con alguna hora
dudosa. Se descartó porque todos los días marcados coincidían con feriados o con lluvia. La lluvia del día es la suma
de la precipitación horaria de ERA5 en la celda de Buenos Aires.

| Fecha | Día | Feriado | Lluvia del día (mm) |
|---|---|---|---|
| 24/03/2022 | jueves | sí | 19,5 |
| 25/05/2022 | miércoles | sí | 21,4 |
| 21/11/2022 | lunes | sí | 7,0 |
| 25/05/2023 | jueves | sí | 10,7 |
| 12/07/2023 | miércoles | no | 20,7 |
| 03/09/2023 | domingo | no | 9,7 |
| 02/11/2023 | jueves | no | 28,0 |
| 21/06/2024 | viernes | sí | 11,3 |
| 31/08/2024 | sábado | no | 41,0 |
| 03/03/2025 | lunes | sí | 84,5 |
| 16/05/2025 | viernes | no | 17,6 |
| 17/05/2025 | sábado | no | 20,7 |
| 14/06/2025 | sábado | no | 16,8 |
| 16/06/2025 | lunes | sí | 2,9 |
| 19/08/2025 | martes | no | 70,8 |
| 31/08/2025 | domingo | no | 16,5 |
