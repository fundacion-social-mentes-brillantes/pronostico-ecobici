# Encargo 27 — Confirmar el margen de redondeo de la prueba del comando de pronóstico

Al subir el encargo 26, la integración continua de GitHub (Linux) falló en
`test_en_las_horas_de_prueba_da_lo_mismo_que_el_experimento`: el comando dio 418,4337321373839 y 185,8520841904485
frente a 418,43373213738204 y 185,85208419044517 guardados (diferencias de 1,9·10⁻¹² y 3,3·10⁻¹² viajes), más que el
margen `abs=1e-12`. En Windows la mayor diferencia es de 8,5·10⁻¹⁴. Es redondeo de punto flotante de cada sistema
(otra biblioteca de álgebra lineal), no un error del comando.

Claude volvió al margen original, `pytest.approx(..., rel=0, abs=1e-9)`, con un comentario que explica por qué, y
cambió «menos de una billonésima» por «menos de una milmillonésima de viaje» en `README.md`, `memoria/anexos.md`
(Anexo B) y el docstring de `src/pronosticar.py`.

Confirma leyendo los archivos (no puedes ejecutar Python) que el margen y los textos coinciden. Responde en español,
breve. Si todo está bien, termina con la línea exacta: SIN ERRORES PENDIENTES.
