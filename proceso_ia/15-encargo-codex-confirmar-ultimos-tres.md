# Encargo 15 — Confirmar los tres últimos arreglos

En tu respuesta 14 (proceso_ia/14-respuesta-codex-confirmacion-final-web-y-pdf.txt) confirmaste todo lo anterior y
señalaste tres errores. Arreglos:

1. Portada del PDF: `memoria/construir_pdf.py`, función `portada()`: el gráfico ya no está oculto; lleva
   `role="img"` y un `aria-label` que lo describe (se ve en `memoria/memoria.html`, ya regenerado, y en el PDF nuevo).
2. `web/index.html` (párrafo bajo «Cinco maneras de pronosticar»): ya no dice que reciben la misma información; dice
   que el *boosting* ve la hora y el día de la semana, y Ridge y el perceptrón la hora combinada con el tipo de día
   (laborable, sábado, o domingo y feriado); los conteos, el mes y los indicadores de feriado y no laborable, todos.
3. Mediana de calendario: `web/index.html` dice «esa hora en ese día de la semana (los feriados cuentan como
   domingo)» y `memoria/glosario.md` añade «los feriados cuentan como domingo» (Word y PDF regenerados).

Revisa solo estos tres puntos (y que no rompan nada alrededor). No puedes ejecutar Python. Responde en español, breve.
Si están bien, termina con la línea exacta: SIN ERRORES PENDIENTES. Si no, di qué falta, con archivo y línea.
