# Encargo 25 — Confirmar los últimos detalles del comando de pronóstico

En el encargo 24 confirmaste los cinco arreglos y señalaste cuatro detalles. Claude los corrigió (aún sin subir):

1. Aviso dentro del ajuste: el aviso general ahora dice que el modelo ya vio esa hora «así que ninguno de estos
   pronósticos es honesto», y un comentario en `imprimir` explica por qué no se repite el aviso de cada escenario.
2. Prueba del caso `2024-05-25 17:00` con 1 h: solo pronostican el ingenuo y la mediana, y a Ridge, perceptrón y
   boosting les falta `ultimo_conteo` (en `test_cada_metodo_pronostica_si_tiene_sus_datos`).
3. Redacción: la Tabla 5.1 ya no dice «ya ajustados»; el capítulo 5, el Anexo B, el README y el docstring dicen «las
   mismas cifras … salvo diferencias de redondeo de menos de una billonésima de viaje» (Claude midió la mayor
   diferencia en las tres horas de la prueba: 8,5·10⁻¹⁴ viajes, en el perceptrón); el LEEME aclara que tres de las
   doce pruebas hacen esa comparación.
4. Anexo A: «veinticuatro encargos»: del 01 al 25 menos el 20 (que es el registro de las ilustraciones y las
   críticas); cuenta el 09 (del que solo se guardó la respuesta) y este 25.

Confirma leyendo el código y los textos (no puedes ejecutar Python). Responde en español, breve, lista numerada. Si
todo está bien, termina con la línea exacta: SIN ERRORES PENDIENTES.
