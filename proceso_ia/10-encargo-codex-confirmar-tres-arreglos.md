# Encargo 10 — Confirmar los tres arreglos de tu respuesta 09

En tu respuesta 09 (proceso_ia/09-respuesta-codex-confirmacion-final.txt) señalaste tres problemas. Los arreglé así:

2. JSON con NaN: `src/tablas_memoria.py` → `redondear()` ahora devuelve `None` para todo valor no finito y el
   archivo se escribe con `allow_nan=False`. `src/experimento.py` → `guardar_json()` pasa por `sin_no_finitos()` y
   también usa `allow_nan=False`. Nueva prueba: `tests/test_estadistica.py::test_los_json_nunca_llevan_nan_ni_infinitos`.
3. Reutilización del número de proceso: `src/serie_horaria.py::extraer` y `src/descargar_datos.py::bajar` usan
   ahora proceso + marca aleatoria (uuid, 12 hex) en los nombres temporales, y abren el temporal con modo `"xb"`
   (falla si ya existiera). `extraer` además comprueba que ni el CSV final ni el temporal existan antes.
4. Plazo de descarga: `inicio` se toma antes de pedir el archivo; el bloque es de 64 KB; el comentario explica
   ahora con exactitud qué se garantiza (detenida → se corta en 120 s; lenta pero avanzando → al primer bloque
   después de la hora).

Comprobé: 15 pruebas pasan; el experimento completo se volvió a correr y predicciones, tablas y contrastes son
idénticos byte a byte (solo cambian los tiempos medidos).

Revisa SOLO estos tres arreglos (y que no rompan nada alrededor). Responde en español, breve. Si todo está bien,
termina con la línea exacta: SIN ERRORES PENDIENTES. Si no, di qué falta, con archivo y línea.
