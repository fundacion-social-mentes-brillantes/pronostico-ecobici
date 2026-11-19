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

Reglas que se siguieron: ninguna referencia sin comprobar en Crossref, arXiv o la página oficial; ninguna cifra que
no salga del código; ninguna columna con datos de personas seleccionada; todo lo que hizo Codex, revisado por Claude
antes de darlo por bueno.
