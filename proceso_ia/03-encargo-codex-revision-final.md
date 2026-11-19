# Encargo para Codex: revisión final del proyecto (segundo lector)

Responde en español. No escribas ni cambies archivos: solo lee y responde. Trabajas en esta carpeta.

Es un proyecto con la forma de un Trabajo Fin de Máster en IA (tipo «comparativa de soluciones»): pronóstico de
viajes horarios de Ecobici Buenos Aires con datos retrasados. Lo dirigió Claude y tú programaste los modelos y
redactaste los capítulos 2 y 3. Ahora revisa TODO como un director de TFM exigente y como revisor de código.

Lee: `memoria/*.md` (resumen, capítulos 1 a 8, referencias y anexos), `memoria/bibliografia_verificada.md`, todo
`src/`, `tests/`, `README.md` y los resultados en `resultados/` (`metricas_prueba.csv`, `metricas_validacion.csv`,
`hiperparametros_elegidos.json`, `diebold_mariano.csv`, `horas_excluidas.json`, `calidad_datos.json`).

Quiero la **lista COMPLETA** de problemas, con archivo y línea (o sección y frase exacta), de más a menos grave, y
para cada uno el arreglo concreto:

1. **Cifras**: cada número de la memoria debe coincidir con los archivos de `resultados/` o con los datos. Comprueba
   todos los de los capítulos 4, 5 y 6 y del resumen. Di cuál no coincide.
2. **Afirmaciones** que no se sostienen con los resultados o con las fuentes (las fuentes válidas son solo las de
   `bibliografia_verificada.md`, y solo para lo que allí dice). Citas en el texto que no estén en las referencias o
   referencias que nadie cita.
3. **Código**: errores, fugas de información del futuro, cosas que no hacen lo que dice la memoria, problemas de
   seguridad (por ejemplo, SQL armado con texto que venga de un archivo, descargas sin tiempo límite, rutas) y
   ineficiencias claras. Revisa que `src/serie_horaria.py` no lea nunca las columnas del usuario.
4. **Coherencia** entre capítulos (por ejemplo, el capítulo 3 escrito en futuro cuando el trabajo ya está hecho,
   repeticiones largas entre los capítulos 2, 3 y 5).
5. **Redacción**: frases confusas, demasiado largas, o con muletillas típicas de IA.

Si algo está bien, no lo menciones. Al final di qué no pudiste comprobar.
