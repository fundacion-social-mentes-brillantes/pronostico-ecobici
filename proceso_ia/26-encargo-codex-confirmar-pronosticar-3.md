# Encargo 26 — Confirmación final del comando de pronóstico

En el encargo 25 quedaron dos detalles. Claude los corrigió (aún sin subir):

1. `README.md` (sección «Pronosticar una hora») ahora dice «salvo diferencias de redondeo de la computadora de menos
   de una billonésima de viaje».
2. `tests/test_pronosticar.py` compara con `pytest.approx(..., rel=0, abs=1e-12)`, el mismo límite que se documenta
   (con Python pasan las 32 pruebas).

Además, para no tener que cambiar la cuenta con cada encargo nuevo, el Anexo A dice ahora «más de veinte encargos»
(como el Léeme de la carpeta), y el LEEME de `proceso_ia/` cita los encargos 23 a 26.

Confirma leyendo los archivos (no puedes ejecutar Python). Responde en español, breve. Si todo está bien, termina con
la línea exacta: SIN ERRORES PENDIENTES.
