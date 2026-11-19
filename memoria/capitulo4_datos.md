# 4. Datos y preparación

Este capítulo describe las fuentes utilizadas, las decisiones de depuración y la serie horaria resultante. Todas
las cifras proceden de los scripts del repositorio (`src/serie_horaria.py`, `src/descargar_clima.py`,
`src/feriados.py`) y de los archivos de control que generan (`resultados/calidad_datos.json`,
`resultados/cobertura_mensual.csv`).

## 4.1. Fuentes

La Tabla 4.1 resume las tres fuentes. Todas son públicas y ninguna contiene información que permita identificar a
una persona en el conjunto finalmente analizado.

**Tabla 4.1.** Fuentes de datos.

| Fuente | Periodo | Formato y tamaño | Uso | Licencia |
|---|---|---|---|---|
| Recorridos de Ecobici (Gobierno de la Ciudad de Buenos Aires, s. f.) | 2022-2025 | Un ZIP por año con un CSV; 701,5 MB comprimidos y 3.261 MB sin comprimir en total | Conteo de viajes iniciados por hora | CC BY 2.5 Argentina |
| Open-Meteo, producto ERA5 (Zippenfenig, 2023) | 25/12/2021-31/12/2025 | API; 35.232 horas | Temperatura y precipitación (análisis secundario) | CC BY 4.0 |
| Feriados y días no laborables de Argentina (Ley 27.399 de 2017; Decreto 573/2022; Decreto 1027/2024; Resolución 139/2025) | 2022-2025 | Calendario construido en `src/feriados.py` | Variables de calendario | Normativa pública |

Los archivos de recorridos se descargaron el 19 de noviembre de 2026 desde el servidor de contenidos del portal
Buenos Aires Data; su tamaño y su huella SHA-256 quedaron registrados en `datos/procesados/manifiesto_descarga.json`.
Cada archivo tiene un nombre y una estructura ligeramente distintos: el de 2022 trae 19 columnas
(incluidas dos columnas de índice sin significado), el de 2023 trae 18 y los de 2024 y 2025 traen 17. Las
diferencias afectan sobre todo a los nombres de columnas (por ejemplo, la columna de género aparece con tilde y
mayúscula en 2022 y sin ellas en 2024). Por eso el script busca cada columna necesaria por su nombre y se detiene
si alguna falta, en lugar de depender de su posición.

## 4.2. Lectura y depuración de los recorridos

### 4.2.1. Columnas leídas

Los archivos publicados incluyen, además de los datos del recorrido, un identificador del usuario, su género y el
modelo de la bicicleta. Para este trabajo solo se seleccionaron cinco columnas: el identificador del recorrido, la
fecha y hora de origen, la fecha y hora de destino y los identificadores de las estaciones de origen y destino (la
duración publicada no se usa: la duración se calcula con las horas de salida y llegada). Las columnas del usuario
nunca se seleccionaron ni pasaron al conjunto analítico, que contiene únicamente conteos por hora. Conviene precisar el alcance: el archivo publicado sí se descomprime completo en disco
mientras dura el proceso, porque así se distribuye, y se borra al terminar. La lectura se hizo con SQL mediante
DuckDB (Raasveldt y Mühleisen, 2019), que permite consultar los CSV directamente sin cargarlos completos en memoria;
la ruta del archivo se pasa a la consulta como parámetro y no como texto.

### 4.2.2. Reglas de depuración

Se aplicaron seis reglas, definidas antes de entrenar ningún modelo; el script cuenta por separado cuántos registros
descarta cada una:

1. Descartar los recorridos cuya fecha de inicio no pudiera interpretarse.
2. Descartar los que empezaran fuera de 2022-2025.
3. Descartar los que no tuvieran hora de llegada (registros incompletos).
4. Descartar los que llegaran antes de salir.
5. Descartar los recorridos de menos de 60 segundos, medidos entre la hora de salida y la de llegada.
6. Descartar los recorridos sin identificador y conservar uno solo de cada identificador repetido.

La quinta regla merece una explicación, porque surgió de la propia revisión de los datos. Al comparar los años se
observó que en los archivos de 2022 y 2023 no hay **ningún** recorrido de menos de 60 segundos (el más corto dura
61 s) y en el de 2025 solo hay 8, mientras que el de 2024 contiene 321.015, el 9,0 % de sus filas. De ellos,
232.507 empiezan y terminan en la misma estación, un patrón compatible con bicicletas retiradas y devueltas de
inmediato, y 28.126 tienen exactamente la misma hora de salida y de llegada entre estaciones distintas, algo que no
puede corresponder a un viaje real. La hipótesis más simple es que el publicador filtra esos registros en los demás
años y no lo hizo en 2024, aunque no se conoce su filtro exacto. Si se conservaran, el nivel de 2024 quedaría
inflado frente a los otros años y un modelo entrenado con 2022-2024 aprendería un salto de demanda que probablemente
no existe. Aplicar el mismo umbral de 60 segundos a los cuatro años es, por tanto, una decisión analítica para
hacerlos comparables. El archivo de 2024 tiene además 3.379 recorridos sin hora de llegada, que se descartan por la
tercera regla.

**Tabla 4.2.** Resultado de la depuración por año.

| Año | Filas del archivo | Inicio inválido o fuera de periodo | Sin hora de llegada | Llegada antes de la salida | Menos de 60 s | Tras depurar |
|---|---|---|---|---|---|---|
| 2022 | 2.922.805 | 0 | 0 | 0 | 0 | 2.922.805 |
| 2023 | 2.622.331 | 0 | 0 | 0 | 0 | 2.622.331 |
| 2024 | 3.559.284 | 0 | 3.379 | 0 | 321.015 | 3.234.890 |
| 2025 | 3.156.182 | 0 | 0 | 0 | 8 | 3.156.174 |
| **Total** | **12.260.602** | **0** | **3.379** | **0** | **321.023** | **11.936.200** |

Nota: ningún recorrido carecía de identificador. Después se eliminó un recorrido repetido (un identificador que
aparecía dos veces con la misma hora de salida) y quedaron **11.936.199** recorridos válidos. Todas las fechas de
inicio caían dentro del año de su archivo.

## 4.3. Serie horaria y cobertura

Los recorridos válidos se agruparon por la hora local de inicio. El resultado se completó con todas las
horas entre el 1 de enero de 2022 a las 00:00 y el 31 de diciembre de 2025 a las 23:00: **35.064 horas**.

Una hora sin recorridos puede ser un cero real o un hueco en los datos. Se marcaron como **cobertura dudosa** dos
casos: toda racha de cuatro o más horas seguidas sin ningún viaje, y toda hora sin viajes entre las 7:00 y las
21:59, porque en esa franja lo normal son decenas o cientos de viajes por hora y un cero es, con mucha
probabilidad, un corte del servicio o del registro. La primera regla encontró un único hueco, de 19 horas, entre el 25 y el 26 de
mayo de 2024. La segunda añadió dos horas: el 25 de mayo de 2024 a las 16:00, junto a ese mismo hueco, y el martes
14 de octubre de 2025 a las 13:00. Las 21 horas quedaron como faltantes. Otras cuatro horas sin viajes, todas entre
la 1:00 y las 5:00, se conservaron como ceros: la regla no permite saber si fueron una ausencia real de viajes o un
fallo breve, pero a esas horas un cero es plausible. La regla de las rachas es una auditoría retrospectiva: para
saber si un cero inicia una racha de cuatro hay que mirar las horas siguientes. En la prueba no tiene efecto, porque
la única hora dudosa de ese periodo la marcó la regla diurna, que no mira hacia adelante.

También se probó una segunda regla: marcar como dudosos los días con menos del 25 % de la mediana del mismo día de
la semana en las cuatro semanas anteriores y posteriores. Marcó 16 días (listados en el Anexo C). Al revisarlos
uno por uno, 7 eran feriados y los otros 9 tuvieron entre 9,7 y 70,8 mm de lluvia: días en los que una caída de la
demanda es esperable. La coincidencia no prueba que el registro de esos días esté completo, pero tampoco da motivo
para tratarlos como fallos. Por ejemplo, el 31 de agosto de 2024, un sábado con 41 mm de lluvia, registró solo
370 viajes, el mínimo del periodo. Eliminar esos días habría quitado precisamente los casos difíciles que un
modelo debe saber pronosticar, así que la regla se descartó. Conviene ser transparente: esta regla miraba las
semanas anteriores y posteriores y marcó también días del periodo de prueba, de modo que las reglas de calidad se
decidieron mirando la serie completa. La decisión se tomó antes de entrenar ningún modelo y sin consultar ningún
error de pronóstico, y queda registrada en el código.

## 4.4. Análisis exploratorio

### 4.4.1. Nivel y estacionalidad anual

La Tabla 4.3 muestra los totales por año. 2023 fue el año de menor uso y 2024 el de mayor, ya depurado. El uso
mensual sigue un patrón estacional claro y repetido: cae en junio y julio, los meses más fríos, y sube en
primavera, de septiembre a noviembre. El mes con más viajes fue octubre de 2025 (344.319) y el de menos, junio de
2025 (150.753), un mes con varios días de lluvia fuerte.

**Tabla 4.3.** Viajes válidos por año (la media por hora se calcula sobre las horas con cobertura válida).

| Año | Viajes | Media por hora |
|---|---|---|
| 2022 | 2.922.805 | 333,7 |
| 2023 | 2.622.331 | 299,4 |
| 2024 | 3.234.889 | 369,1 |
| 2025 | 3.156.174 | 360,3 |

{{FIGURA:01_viajes_diarios}}

### 4.4.2. Ciclo semanal y diario

La diferencia entre días laborables y fines de semana es la característica más marcada de la serie. Contando solo
los días con las 24 horas válidas de 2022-2025, un día laborable tiene en promedio 10.247 viajes; un sábado, 3.811;
un domingo, 3.834, y un feriado, 4.260. El perfil horario también cambia de forma (Figura 4.2, bloque 2022-2024): en
los laborables el uso sube con fuerza desde las 6:00, tiene un
primer máximo a las 8:00 (545 viajes por hora de media), baja a media mañana, vuelve a subir al mediodía y alcanza
el máximo a las 17:00 y 18:00 (949 y 933). Los sábados, y también los domingos y feriados, el uso crece despacio a lo
largo del día y llega a su máximo a las 16:00 (326 y 362 viajes por hora de media), sin pico de mañana. Las seis horas con mayor media en días laborables del bloque 2022-2024 son las 13:00, 15:00, 16:00,
17:00, 18:00 y 19:00; son las que se usan como **horas pico** en la evaluación. La hora con más viajes de todo el
periodo fue el 10 de noviembre de 2025 a las 18:00 (1.527 viajes).

{{FIGURA:02_perfil_horario}}

Este patrón justifica dos decisiones del diseño. Primero, que Ridge y el perceptrón reciban la combinación de hora y
tipo de día, y no solo la hora: la misma hora significa cosas distintas un martes y un domingo. Segundo, que los
feriados se agrupen con los domingos en el tipo de día: su nivel (4.260 viajes diarios) se parece mucho más al de un
domingo que al de un laborable, aunque es algo mayor, sobre todo cuando el feriado cae entre semana (4.531).

### 4.4.3. Dependencia temporal

La autocorrelación mide cuánto se parece la serie a sí misma desplazada en el tiempo. Con un desfase de una hora
vale 0,93; con 24 horas, 0,75, y con 168 horas (una semana), 0,85. Que la correlación semanal sea mayor que la
diaria tiene sentido: el día anterior puede ser de otro tipo (un lunes comparado con un domingo), mientras que la
semana anterior siempre corresponde al mismo día. Estas cifras adelantan lo que se mide en el experimento: con
datos de hace una hora hay mucha información útil, y al alejarse el último dato, la referencia semanal gana peso
relativo.

### 4.4.4. Lluvia y demanda

Los días de lluvia registraron menos viajes. Entre los días laborables con las 24 horas válidas, los 762 días
prácticamente secos (menos de 1 mm) tuvieron en promedio 10.728 viajes, y los 69 días con 10 mm o más, 6.990: un
35 % menos. Es una comparación
descriptiva, que no controla otros factores como la estación del año, pero muestra que el clima contiene
información relevante para el análisis secundario.

## 4.5. Clima

La consulta a Open-Meteo devolvió la celda del producto ERA5 centrada en -34,5° de latitud y -58,5° de longitud
(rejilla de 0,25°), que cubre el centro de Buenos Aires, a 18 m de altitud, sin ninguna hora faltante; el script
comprueba que la rejilla horaria esté completa y sin repeticiones. Según la documentación de la API (Zippenfenig, 2023), la
temperatura es el valor instantáneo de la hora indicada y la precipitación es la suma de la hora anterior a la etiqueta; por eso,
para el intervalo de 10:00 a 11:00 se usa la temperatura de las 10:00 y la precipitación etiquetada a las 11:00.
Hubo precipitación en 4.430 de las 35.064 horas del periodo (12,6 %) y en 484 de las 4.244 horas evaluadas en la
prueba. La consulta exacta, la celda y la fecha de extracción quedaron guardadas en
`datos/procesados/clima_meta.json`.

## 4.6. Feriados y días no laborables

El calendario se construyó con la librería `holidays` y se corrigió con lo efectivamente aplicado según la Ley
27.399 de 2017 y las normas aplicables a cada año. El Jueves Santo se clasificó como día no laborable en los cuatro
años. Se añadió el feriado nacional del 2 de septiembre de 2022 (Decreto 573/2022). En 2025 se trasladó el feriado
del 12 de octubre (domingo) al viernes 10 (Resolución 139/2025) y se clasificaron el 2 de mayo, el 15 de agosto y
el 21 de noviembre como días no laborables con fines turísticos (Decreto 1027/2024). El calendario incluye también
los dos feriados extraordinarios de 2022
que recoge la librería: el del Censo Nacional (18 de mayo) y el de la celebración de la Copa Mundial (20 de
diciembre). Estos dos no se cotejaron con las normas que los establecieron. En total hay 76 feriados y 7 días no laborables en los
cuatro años.

## 4.7. Conjunto resultante

El conjunto analítico es una tabla de 35.064 filas, una por hora, con el número de viajes iniciados (o un valor
faltante en las 21 horas dudosas), la temperatura y la precipitación, y los indicadores de calendario. Ocupa poco
más de 1 MB y se incluye en el repositorio (`datos/procesados/`), de modo que los experimentos pueden repetirse sin
descargar de nuevo los 701,5 MB de recorridos. Los recorridos originales se obtienen con `src/descargar_datos.py`.
