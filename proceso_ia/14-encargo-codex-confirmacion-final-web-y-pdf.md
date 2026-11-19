# Encargo 14 — Confirmación final de la web y del PDF

En tu respuesta 13 (proceso_ia/13-respuesta-codex-verificar-web-y-revisar-pdf.txt) confirmaste los puntos 1 a 9 y 14
y dejaste pendientes el 10 al 13. Ya está todo subido (commit e6e54f1) y la página publicada en
https://fundacion-social-mentes-brillantes.github.io/pronostico-ecobici/ (GitHub Pages copia `web/` y la memoria).

Arreglos:

10. Las copias `web/memoria.pdf` y `web/memoria.docx` son copias locales que no se suben (están en `.gitignore`);
    se actualizaron con la memoria nueva, que ya no lleva el nombre de pila. La página publicada toma la memoria de
    `memoria/` en el flujo `.github/workflows/pagina.yml`.
11. `web/app.js` (función `dibujarSemanas`): el máximo del eje ignora los `null` y una semana con algún MAE `null` no
    dibuja ni puntos ni línea.
12. `memoria/construir_pdf.py`: en los capítulos y anexos, el número grande va en un `div.num-capitulo` aparte y dentro
    del título queda «1. » casi invisible (`.oculto`); además, `corregir_marcadores()` reescribe con pypdf el título de
    cada marcador con su texto exacto, porque Chrome juntaba las palabras donde el título cambiaba de renglón. Los 83
    marcadores quedaron limpios («1. Introducción», «1.1 Motivación», «Anexo A. …»).
13. `memoria/construir_docx.py` (`TOKEN`, que usan el Word y el PDF): las URL admiten paréntesis equilibrados, así que
    el DOI de Tashman queda entero (también en el Word); la suma se escribe `∑` (U+2211) y no la letra `Σ`; cada figura
    del PDF lleva como texto alternativo su pie (`alt`).

Comprueba esos cuatro puntos y haz una última pasada general, leyendo:
- `web/index.html`, `web/app.js`, `web/estilos.css`, `src/exportar_web.py`;
- `memoria/construir_pdf.py`, `memoria/estilo_pdf.css`, `memoria/memoria.html` (el documento intermedio, que ya trae
  todo el contenido del PDF), `memoria/capitulo5_implementacion.md` (5.4 y 5.6 cambiaron: veinte pruebas y el tiempo
  medido con el equipo libre), `README.md` y `memoria/anexos.md` (Anexo B).

Señala solo errores reales (de código, de exactitud, de accesibilidad o de presentación), con archivo y línea. No
puedes ejecutar Python. Responde en español, breve. Si todo está bien, termina con la línea exacta:
SIN ERRORES PENDIENTES.
