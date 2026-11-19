# Encargo 13 — Verificar los arreglos de la web y revisar el PDF y las figuras

## 1. Tus 11 puntos de la respuesta 12 (proceso_ia/12-respuesta-codex-revisar-web.txt)

Claude los atendió así; confirma cada uno leyendo el código:

1. Foco de los botones de edad: contorno de tinta con desplazamiento interior; en el botón activo, color papel
   (`web/estilos.css`, reglas `.segmentos button:focus-visible`).
2. Escape cierra el globo desde cualquier parte del documento (`web/app.js`, escucha de `keydown` en `document`).
   El globo no captura el puntero y se mantiene mientras el puntero esté sobre el gráfico.
3. Los puntos de la tira de semanas ya no tapan el clic (`.puntos-semana { pointer-events: none }`). Hay una tabla
   alternativa con las 26 semanas y un botón «Ver arriba» por fila (accesible con teclado). Los gráficos tienen
   `aria-label` con sus cifras (perfil, resultados, semanas, clima, tramos).
4. Semana final de dos días: el puntero más allá del último dato oculta el globo; se rotula «Fin del periodo de prueba».
5. Horas excluidas: el globo dice «Hora fuera de la comparación: su conteo, o uno que el modelo necesitaba, quedó
   marcado como dudoso».
6. El globo usa siempre los valores exactos del retraso elegido (el punto sigue la línea animada); si se activa la
   reducción de movimiento durante la transición, termina de inmediato. La entrada de la portada bajó a 500 ms y quedó
   documentada en `DESIGN.md`.
7. a 9. Textos corregidos en `web/index.html` («Lo habitual es…», «Lo más probable es que el publicador…», «con mucha
   probabilidad, cortes…», «se evalúan, ya congelados y sin reajustarlos», días no laborables y codificación propia
   de cada modelo, «una sola semilla», «probablemente porque…», y «cuánto ayudaría con uno real no se midió»).
10. El nombre de pila se quitó de la portada del Word y del PDF, del Anexo A y del README. La imagen `web/compartir.png`
    se está generando ahora.
11. `src/exportar_web.py`: el calendario sale del protocolo (8 de julio a 31 de diciembre); las horas faltantes
    quedan en null; las semanas sin datos no entran al cálculo; la semana típica y el conteo «crece» usan MAE sin
    redondear. Resultado: 30 sep – 6 oct y 23 de 26, como calculaste.

## 2. Revisión nueva

- `memoria/construir_pdf.py` y `memoria/estilo_pdf.css`: arman `memoria/memoria.pdf` (54 páginas) desde los
  mismos Markdown que el Word, con Edge sin ventana, dos pasadas para los números del índice (leídos de los
  marcadores del PDF) y las letras incrustadas. El HTML intermedio queda en `memoria/memoria.html`; léelo si te
  sirve. Busca errores reales: conversión de Markdown (listas, tablas, fórmulas `mate()`, enlaces, bloques de código),
  títulos que no casen con los marcadores, casos que rompan la impresión, accesibilidad básica del PDF.
- `src/graficos.py`: las seis figuras con el nuevo estilo (PNG para el Word y SVG para el PDF). Confirma que cada
  figura sigue mostrando lo que dice su pie en `memoria/figuras.txt` y lo que cuenta el texto de los capítulos 4 y 6.

No puedes ejecutar Python. Responde en español, breve, como lista numerada con archivo y línea. Si todo está bien,
termina con la línea exacta: SIN ERRORES PENDIENTES.
