# 5. Implementación de la comparativa

Este capítulo describe cómo se llevó a código el diseño del capítulo 3 y qué decisiones concretas fue necesario
tomar al implementarlo. El objetivo es que cualquier lector pueda comprobar que el código hace lo que la
metodología dice, y repetirlo.

## 5.1. Organización del código

El proyecto se organizó como una canalización de scripts pequeños, cada uno con una sola responsabilidad, en
lugar de un cuaderno largo. La Tabla 5.1 resume los módulos. Las rutas, las particiones, el margen, los retrasos y
la semilla se leen de un único archivo de configuración (`src/config.py`).

**Tabla 5.1.** Módulos del proyecto.

| Módulo | Responsabilidad |
|---|---|
| `config.py` | Rutas, zona horaria, particiones, margen de siete días, retrasos {1, 24, 168} y semilla |
| `descargar_datos.py` | Descarga de los ZIP a un archivo temporal, comprobación de tamaño y manifiesto con huellas SHA-256 |
| `serie_horaria.py` | Lectura con SQL (DuckDB), depuración con recuento por motivo, agregación horaria y marcas de cobertura |
| `descargar_clima.py`, `feriados.py` | Clima horario de ERA5 (con validación de la rejilla horaria) y calendario de feriados |
| `variables.py` | Variables de calendario y de conteo de cada escenario |
| `modelos.py` | Las cinco alternativas (y la variante con clima) con una interfaz común `ajustar` / `predecir` |
| `estadistica.py` | Métricas, prueba de Diebold-Mariano con varianza de Newey-West y corrección de Holm |
| `experimento.py` | Protocolo completo: búsqueda en validación, ajuste final, prueba y contrastes |
| `graficos.py`, `tablas_memoria.py` | Figuras y tablas complementarias de la memoria, calculadas desde los resultados guardados |
| `ejecutar_todo.py` | Ejecuta experimento, figuras y tablas, y guarda un registro con fecha, versiones, equipo y tiempos |

La interfaz común es la decisión de diseño más útil del código: cada alternativa, desde el ingenuo semanal hasta
el perceptrón, ofrece los mismos dos métodos, `ajustar(datos)` y `predecir(datos)`, y el protocolo de evaluación las
recorre todas con el mismo procedimiento. Así se reduce el riesgo de que una alternativa reciba, por descuido, un
tratamiento distinto al de las demás.

## 5.2. Construcción de las variables

Todas las variables se calculan sobre una rejilla horaria completa, sin huecos: las horas de cobertura dudosa
existen como filas, pero con el conteo vacío. Así, desplazar la serie *d* posiciones equivale exactamente a
retroceder *d* horas reales, algo que no se cumpliría si las horas faltantes se hubieran eliminado. Con esa rejilla:

- `ultimo_conteo` es la serie desplazada *d* posiciones, es decir, $y_{t-d}$;
- `media_24` es la media móvil de 24 posiciones calculada sobre `ultimo_conteo`, de modo que su último valor es
  $y_{t-d}$; se exige un mínimo de 18 valores;
- `semana_anterior` es la serie desplazada 168 posiciones, $y_{t-168}$.

Con 168 horas de retraso, `ultimo_conteo` y `semana_anterior` coinciden. Se mantuvieron ambas columnas para que el
protocolo fuera idéntico en los tres escenarios; el efecto de esa columna duplicada sobre Ridge y el perceptrón se
comenta entre las limitaciones (sección 7.4).

## 5.3. Las alternativas en el código

La Tabla 5.2 resume qué recibe cada alternativa. Las referencias son deliberadamente simples: el ingenuo semanal
devuelve `semana_anterior`, y la mediana de calendario calcula con el bloque de ajuste una tabla de medianas por hora
y día de la semana, en la que los feriados se asignan al domingo.

**Tabla 5.2.** Entradas y codificación de cada alternativa.

| Alternativa | Calendario | Conteos | Objetivo |
|---|---|---|---|
| Ingenuo semanal | — | $y_{t-168}$ | — |
| Mediana de calendario | Hora y día de la semana (feriado = domingo) | — | — |
| Ridge y perceptrón | 72 indicadores de hora × tipo de día (feriado = domingo; no laborable = laborable), 12 de mes, indicadores de feriado y de no laborable | Los tres, en $\log(1+x)$ y estandarizados | $\log(1+y)$; en el perceptrón, además estandarizado |
| *Boosting* | Hora, día de la semana real y mes como categorías; indicadores de feriado y de no laborable | Los tres, en $\log(1+x)$ | $\log(1+y)$ |
| *Boosting* con clima | Como el *boosting*, más la temperatura y la precipitación de ERA5 de la hora pronosticada | Como el *boosting* | Como el *boosting* |

Los estandarizadores se ajustan solo con el bloque de ajuste y se aplican tal cual a validación y prueba. Ridge y el
perceptrón usan las implementaciones de scikit-learn (Pedregosa et al., 2011). La parada temprana del perceptrón es
la interna de scikit-learn: aparta al azar el 10 % de las filas de ajuste y detiene el entrenamiento cuando su
coeficiente de determinación deja de mejorar. Es un control interno, distinto de la validación cronológica, y su
carácter aleatorio se discute entre las limitaciones.

El *boosting* usa `HistGradientBoostingRegressor`, que trata de forma nativa la hora, el día de la semana y el mes
como variables categóricas. Se fijaron 300 iteraciones sin parada temprana para que todas las configuraciones
tuvieran el mismo presupuesto. Las tres alternativas ajustadas devuelven $\exp(\hat z)-1$, recortado en cero.

Las filas usadas para ajustar Ridge, el *boosting* y el perceptrón son las mismas: las del bloque con el objetivo y
las tres variables de conteo completos. Aunque el *boosting* admite faltantes, darle filas distintas habría
mezclado el efecto del modelo con el de los datos.

## 5.4. Pruebas automáticas

El riesgo principal de este trabajo es usar sin querer información del futuro: un error así no produce ningún
fallo visible, solo resultados mejores de lo que deberían. Por eso se escribieron catorce pruebas automáticas
(`tests/`), que se ejecutan con `pytest` en pocos segundos y también en el servicio de integración continua del
repositorio cada vez que se sube un cambio:

1. **Ninguna variable de conteo usa horas posteriores al corte** (una prueba por retraso). Sobre una serie
   sintética, se suman 5.000 viajes a todas las horas entre *t*−*d*+1 y *t* y se comprueba que las variables en *t*
   no cambian, que `ultimo_conteo` vale $y_{t-d}$, que `media_24` es la media de $y_{t-d-23}$ a $y_{t-d}$ y que
   `semana_anterior` vale $y_{t-168}$.
2. **La media de 24 horas exige al menos 18 valores**, y deja de existir con 17.
3. **La mediana de calendario solo usa el bloque de ajuste** y agrupa los feriados con los domingos.
4. **Diebold-Mariano**: da un estadístico nulo con pérdidas iguales; coincide con un caso calculado a mano con un
   rezago de Bartlett; respeta los huecos de la rejilla horaria; rechaza posiciones repetidas o pérdidas no
   finitas, y no inventa significación cuando la varianza es nula.
5. **Holm** ajusta y ordena correctamente los valores p.
6. **Lectura y depuración de los recorridos**: solo se seleccionan las cinco columnas necesarias aunque el archivo
   traiga las del usuario; la lectura funciona aunque la carpeta tenga un apóstrofo en el nombre; y, sobre un archivo
   sintético con un caso de cada tipo, la depuración cuenta cada motivo de descarte una sola vez y la tabla limpia
   solo conserva el identificador y la hora de salida.
7. **Extracción de los ZIP**: se rechaza un ZIP con más de un CSV, y el nombre interno del ZIP nunca se usa como
   ruta (un nombre malicioso como `../../fuera.csv` no puede escribir fuera de la carpeta de datos).

Su utilidad quedó demostrada durante la propia verificación, en dos ocasiones. La prueba de la depuración detectó
que el contador de recorridos de menos de 60 segundos también contaba los que llegan antes de salir (en los datos
reales no había ninguno, así que las cifras no cambiaron). Y la prueba de la mediana falló la primera vez y destapó
un error real. El índice temporal de la tabla y la columna con la hora del día se llamaban igual («hora»), y la
biblioteca de análisis de datos no podía decidir por cuál agrupar. El error habría detenido el experimento; se
corrigió renombrando el índice como «instante».

## 5.5. Selección de configuraciones

La búsqueda de hiperparámetros probó 4 configuraciones de Ridge, 6 de *boosting* y 4 del perceptrón en cada
escenario, eligiendo la de menor MAE en validación (8 de enero a 30 de junio de 2025). La Tabla 5.3 muestra las
elegidas.

**Tabla 5.3.** Configuraciones elegidas en validación.

| Método | 1 h | 24 h | 168 h |
|---|---|---|---|
| Ridge (penalización α) | 1 | 10 | 0,1 |
| *Boosting* (tasa de aprendizaje; hojas máximas) | 0,05; 63 | 0,05; 15 | 0,05; 15 |
| Perceptrón (capas ocultas; α) | 64 y 32; 0,001 | 64 y 32; 0,001 | 64; 0,001 |

En el *boosting*, con datos de hace una hora la validación prefirió árboles más grandes que con datos de hace
un día o una semana. La tasa de aprendizaje elegida fue la misma en los tres escenarios. Una lectura posible es
que, con menos señal reciente, los árboles más pequeños aprenden menos ruido. La Tabla 5.4
muestra el error de validación de la configuración elegida.

**Tabla 5.4.** MAE de validación (8 de enero a 30 de junio de 2025), en viajes por hora.

| Método | 1 h | 24 h | 168 h |
|---|---|---|---|
| Ingenuo semanal | 106,63 | 106,63 | 106,63 |
| Mediana de calendario | 105,43 | 105,43 | 105,43 |
| Ridge | 37,17 | 85,39 | 92,99 |
| *Boosting* | 31,65 | 72,54 | 86,96 |
| Perceptrón | 32,80 | 78,77 | 86,31 |

## 5.6. Ejecución y coste computacional

Todo el proyecto corre en un computador personal con 24 núcleos lógicos, sin GPU (el detalle del equipo y de las
versiones de las librerías queda en `resultados/registro_ejecucion.json`). Construir la serie a partir de los cuatro
ZIP, incluida la extracción de los 3,2 GB de CSV, tarda unos 25 segundos; DuckDB recorre cada tabla una sola vez
para todos los contadores de calidad, y los CSV extraídos se borran en cuanto dejan de hacer falta. El experimento
completo, con la búsqueda de configuraciones de los tres escenarios, el ajuste final, la prueba, los contrastes, las
seis figuras y las tablas complementarias, tardó **29,24 segundos** en la última ejecución.

Durante el experimento se limitó a un hilo el paralelismo interno de las bibliotecas numéricas, para que los
tiempos de ajuste fueran comparables entre métodos. En los ajustes finales, Ridge tardó unas 0,03 s, el *boosting*
de 0,3 a 0,6 s, el *boosting* con clima de 0,4 a 0,7 s y el perceptrón de 1,3 a 1,5 s. En la búsqueda de
validación, los ajustes tardaron de 0,028 a 0,048 s para Ridge, de 0,3 a 0,6 s para el *boosting* y de 0,8 a 1,3 s para
el perceptrón. Pronosticar las 4.244 horas de prueba tardó menos de una décima de segundo con cualquiera de ellos.

La primera repetición confirmó la reproducibilidad tras las correcciones de robustez. El registro citado arriba
corresponde a la ejecución final con el calendario corregido (véase el capítulo 6).
