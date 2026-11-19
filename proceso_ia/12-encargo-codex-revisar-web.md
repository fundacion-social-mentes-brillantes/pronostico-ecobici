# Encargo 12 — Revisar la página web del proyecto

Claude construyó la página pública del estudio (se publicará en GitHub Pages desde `web/`):

- `web/index.html`, `web/estilos.css`, `web/app.js` (gráficos SVG dibujados a mano, sin librerías),
  `web/datos.js` (generado por `src/exportar_web.py` a partir de `resultados/` y `datos/procesados/`).
- `tests/test_web.py` comprueba que `datos.js` está al día y que las 39 cifras escritas en el HTML (atributo
  `data-cifra`) coinciden con los datos. Contrato de diseño: `DESIGN.md`.

Revisa como un revisor exigente y señala SOLO problemas reales, con archivo y línea:

1. **Errores de JavaScript** o casos que rompen: semanas incompletas (la última tiene 48 horas), horas sin dato
   (null), cambio rápido de edad o de semana durante la animación, redimensionar, teclado (flechas, Inicio, Fin,
   Escape), toque en celular, modo oscuro, `prefers-reduced-motion`.
2. **Accesibilidad** (WCAG 2.2 AA): roles y nombres, `aria-pressed`, regiones `aria-live`, foco visible, orden de
   tabulación, textos alternativos de los gráficos, contraste de los colores de `estilos.css` en claro y oscuro.
3. **Exactitud del texto**: cada afirmación de `index.html` debe estar respaldada por `memoria/` o `resultados/`
   (por ejemplo: «Elegir entre modelos competentes cambió el error alrededor de un 10 %», «perder la hora más reciente
   lo multiplicó por dos y medio», las tres semanas excepcionales, «Trescientos árboles», los métodos y variables,
   las limitaciones). Señala lo que esté mal, exagerado o sin respaldo.
4. **Seguridad y privacidad**: `innerHTML` solo con datos propios; ningún recurso externo; nada personal.
5. **`src/exportar_web.py`**: que la regla de la semana típica y el conteo de semanas en que «el error crece» sean
   correctos y que no haya errores de bordes (fechas, horas faltantes).

No puedes ejecutar Python en tu entorno; lee el código. No propongas cambios de estilo ni de gusto. Responde en
español, breve, como lista numerada. Si no encuentras nada, termina con la línea exacta: SIN ERRORES PENDIENTES.
