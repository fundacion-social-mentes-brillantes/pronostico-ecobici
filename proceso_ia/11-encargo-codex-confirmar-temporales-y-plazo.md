# Encargo 11 — Confirmar los dos retoques de tu respuesta 10

En tu respuesta 10 (proceso_ia/10-respuesta-codex-confirmar-tres-arreglos.txt) aprobaste el arreglo 2 y señalaste:

3. Si `open(..., "xb")` falla, el `finally` podía borrar un temporal ajeno. Ahora `extraer` (src/serie_horaria.py) y
   `bajar` (src/descargar_datos.py) abren primero el temporal con "xb", marcan `creado = True` justo después, y el
   `finally` solo borra si `creado`. En `bajar` el temporal se abre antes de pedir el archivo.
4. Plazo: `bajar` vuelve a comprobar el plazo total al salir del bucle, antes de aceptar el ZIP.

Dos pruebas nuevas en tests/test_datos.py (`test_extraer_no_borra_un_temporal_ajeno`,
`test_la_descarga_no_borra_un_temporal_ajeno`) fijan la marca aleatoria, crean el temporal "ajeno" antes y
comprueban que se lanza FileExistsError y que el archivo ajeno sigue intacto. Las 17 pruebas pasan (las corrí yo,
porque tu entorno no puede ejecutar Python).

Revisa SOLO estos dos retoques. Responde en español y breve. Si están bien, termina con la línea exacta:
SIN ERRORES PENDIENTES. Si no, di qué falta, con archivo y línea. No señales mejoras opcionales.
