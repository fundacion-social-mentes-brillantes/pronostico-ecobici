# Encargo 24 — Confirmar los arreglos del comando de pronóstico

En el encargo 23 señalaste cinco puntos de `src/pronosticar.py`. Claude los corrigió así (aún sin subir):

1. Honestidad: cada escenario lleva `honesto = corte >= FIN_AJUSTE` (corte = hora − retraso; `FIN_AJUSTE` =
   2025-06-30 23:00). Si no es honesto, `imprimir` lo avisa en ese escenario. El aviso general de «el modelo ya vio
   esta hora» sigue para horas hasta el fin del ajuste.
2. Caché: la clave es (retraso, hiperparámetros en JSON ordenado, huella `hash_pandas_object` del bloque de ajuste).
3. Sin mínimo global de ocho días: solo se rechazan horas anteriores al inicio de la serie o posteriores al último dato
   más una semana (ahí ya ningún escenario es posible); el resto lo decide cada método según sus datos.
4. Cada método pronostica si tiene sus conteos (`REQUISITOS`: boosting, perceptrón y Ridge, los tres; ingenuo, el de
   hace una semana; mediana, ninguno). Los que no, salen como «sin pronóstico: no hay …». Si el corte es posterior al
   último dato publicado, el escenario entero sigue sin pronóstico (no se podría estar en ese momento).
5. `leer_hora` exige fecha y hora (`AAAA-MM-DD HH[:MM]`, con espacio o T, sin zona horaria) y `pronosticar` rechaza
   instantes con zona horaria.

`tests/test_pronosticar.py` tiene ahora 12 pruebas (con Python pasan las 32 del proyecto), entre ellas tus ejemplos:
`2025-07-03 00:00` (honesto con 1 y 24 h, no con 168 h), `2024-05-25 17:00` con 1 h (solo ingenuo y mediana),
`2022-01-08 17:00` (los cinco métodos en los tres escenarios), `2025-12` y `…18:00-03:00` rechazados.
También se actualizaron `README.md`, `memoria/capitulo5_implementacion.md` (Tabla 5.1 y punto 10 de las pruebas,
ahora dicen «treinta y dos»), `memoria/anexos.md` (Anexo A y B) y `proceso_ia/LEEME.md`.

Confirma leyendo el código (no puedes ejecutar Python) que los cinco puntos quedaron bien y que no se introdujo un
error nuevo; revisa también que las cifras y textos de la documentación coincidan con el código. Responde en español,
breve, lista numerada. Si todo está bien, termina con la línea exacta: SIN ERRORES PENDIENTES.
