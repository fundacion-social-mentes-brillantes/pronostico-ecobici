# Cómo trabajaron Claude y Codex

Este proyecto fue una prueba: llevar de principio a fin, solo con asistentes de IA, un trabajo con la forma de un
Trabajo Fin de Máster en Inteligencia Artificial. Lo dirigió **Claude** (Anthropic, Claude Opus 5.5) y le encargó
partes a **Codex** (OpenAI) desde la línea de comandos. Aquí están los encargos que recibió Codex y lo que
respondió, tal cual.

| Paso | Quién | Qué |
|---|---|---|
| Elegir el tema | Claude y Codex por separado | Cada uno propuso temas sin ver los del otro (Claude 4, Codex 3); se compararon por facilidad, defensa, datos, originalidad y riesgo, comprobando datos y referencias. El tema de las bicicletas lo propuso Codex con datos de Washington; Claude lo pasó a Ecobici Buenos Aires 2022-2025 |
| Revisar la propuesta | Codex (GPT-6.2 Sol) | Revisión como si fuera un director exigente: 24 observaciones, casi todas aplicadas |
| Datos | Claude | Descarga, lectura con SQL, depuración (incluido el hallazgo de los recorridos de menos de un minuto de 2024), clima y feriados |
| Código de los modelos | Codex (GPT-6.2 Sol) | `01-encargo-codex-modelos.md`: variables, cinco modelos, protocolo, Diebold-Mariano, figuras y pruebas. Su entorno aislado no pudo ejecutar el Python del proyecto; Claude ejecutó todo, encontró y corrigió un error (índice y columna con el mismo nombre) y verificó los resultados |
| Capítulos 2 y 3 | Codex (GPT-6.1 Terra) | `02-encargo-codex-capitulos-2-3.md`: estado del arte y metodología, citando solo la bibliografía comprobada; `04-…`: ajuste de ambos capítulos ya con los resultados |
| Resto de la memoria | Claude | Capítulos 1 y 4 a 8, resumen y anexos, con las cifras de la ejecución |
| Revisión final | Codex (GPT-6.2 Sol) | `03-…`: revisión de la memoria y del código completos, 30 observaciones. Claude verificó cada una: corrigió cifras, contó por separado los 3.379 recorridos sin llegada, reforzó la seguridad del código, agregó pruebas y moderó afirmaciones; lo que habría exigido volver a evaluar la prueba quedó como limitación |
| Confirmaciones | Codex (GPT-6.2 Sol) | `05-…` a `11-…`: rondas cortas de verificación después de cada tanda de arreglos (cifras actualizadas tras el feriado del 2/9/2022, JSON sin NaN, nombres temporales únicos, plazo de descarga). Se repitió hasta que Codex respondió «SIN ERRORES PENDIENTES» (encargo 11) |
| Página web y PDF | Claude (diseño y construcción), Codex (GPT-6.2 Sol, revisión) | Claude diseñó y construyó la página (`web/`), el PDF de la memoria y las figuras con un mismo sistema (`DESIGN.md`). Codex revisó la web (`12-…`: 11 puntos de accesibilidad, exactitud de los textos y casos límite), luego el PDF y las figuras (`13-…`, `14-…`) y confirmó cada tanda de arreglos hasta responder «SIN ERRORES PENDIENTES» (encargo 15) |
| Estilo final | Quien encargó el estudio (elección), Codex (ilustraciones y críticas), Claude (construcción) | Claude preparó tres direcciones con vista previa y quien encargó el estudio escogió «Ciudad de noche». Codex hizo las cuatro ilustraciones y criticó las capturas como director de arte en tres rondas (7,5 → 8,5 → nota final); Claude aplicó cada observación. Codex revisó el código del nuevo estilo (`16-…`) y confirmó los arreglos (`17-…`, `18-…`). Las órdenes de las ilustraciones y las críticas, tal cual, están en `20-ilustraciones-y-criticas-codex.md`; el `19-…` y el `21-…` confirman el Anexo A. Del encargo 09 solo se guardó la respuesta |
| Pronóstico de una hora | Claude (código y pruebas), Codex (GPT-6.2 Sol, revisión) | Con el trabajo terminado, quien lo revisaba preguntó por el «predict». Los modelos ya predecían (las 4.244 horas de prueba), pero no había un comando para pedir el pronóstico de una hora concreta: Claude escribió `src/pronosticar.py` y doce pruebas (tres comprueban que da lo mismo que el experimento; las demás, el alcance después del último dato, los avisos y la lectura de la fecha), y Codex lo revisó y confirmó los arreglos (`23-…` a `27-…`) |

Reglas que se siguieron: ninguna referencia sin comprobar en Crossref, arXiv o la página oficial; ninguna cifra que
no salga del código; ninguna columna con datos de personas seleccionada; todo lo que hizo Codex, revisado por Claude
antes de darlo por bueno.
