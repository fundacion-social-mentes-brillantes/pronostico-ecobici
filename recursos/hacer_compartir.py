"""Genera web/compartir.png (1200 × 630), la imagen que muestran WhatsApp y las redes al compartir el enlace.

Usa el mismo sistema que la web y el PDF: letras de web/fuentes y el gráfico de la semana típica de la portada de la
memoria (memoria/construir_pdf.py). Se dibuja con Edge o Chrome sin ventana.
Uso: .venv/Scripts/python recursos/hacer_compartir.py
"""
import base64
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "memoria"))
from construir_pdf import grafico_portada, navegador  # noqa: E402


def fuente(nombre):
    return base64.b64encode((RAIZ / "web" / "fuentes" / nombre).read_bytes()).decode()


def main():
    svg, _ = grafico_portada(ancho=1080, alto=250)
    svg = svg.replace('width="1080mm" height="250mm"', 'width="1080" height="250"')
    pagina = f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><style>
@font-face {{ font-family: N; src: url(data:font/woff2;base64,{fuente("Newsreader-VF.woff2")}) format("woff2"); font-weight: 200 800; }}
@font-face {{ font-family: S; src: url(data:font/woff2;base64,{fuente("SchibstedGrotesk-VF.woff2")}) format("woff2"); font-weight: 400 900; }}
html, body {{ margin: 0; width: 1200px; height: 630px; overflow: hidden; background: #f4f3ef; color: #1a1d21; }}
.caja {{ box-sizing: border-box; width: 1200px; height: 630px; padding: 54px 60px 40px; display: flex; flex-direction: column; }}
h1 {{ margin: 0; font-family: N; font-weight: 540; font-size: 66px; line-height: 1.02; letter-spacing: -0.02em; max-width: 900px; text-wrap: balance; }}
p {{ margin: 18px 0 0; font-family: S; font-size: 23px; line-height: 1.35; color: #4f555d; max-width: 980px; }}
svg {{ display: block; margin-top: auto; overflow: visible; }}
path {{ fill: none; stroke-linejoin: round; stroke-linecap: round; }}
.p-real {{ stroke: #1a1d21; stroke-width: 3.2; }} .p-1 {{ stroke: #0f6f63; stroke-width: 2; }}
.p-24 {{ stroke: #965806; stroke-width: 2; }} .p-168 {{ stroke: #ae3b2f; stroke-width: 2; }}
.dias line {{ stroke: #d6d3ca; stroke-width: 1.2; }}
.pie {{ margin-top: 16px; font-family: S; font-size: 17px; color: #62686f; display: flex; gap: 22px; align-items: center; }}
.m {{ display: inline-block; width: 28px; height: 3px; margin-right: 8px; vertical-align: middle; }}
</style></head><body><div class="caja">
<h1>El dato fresco pesa más que el modelo.</h1>
<p>Pronóstico de viajes de Ecobici, en Buenos Aires, con el último conteo de hace una hora, un día o una semana.</p>
{svg}
<div class="pie"><span><span class="m" style="background:#1a1d21;height:4px"></span>Viajes reales</span>
<span><span class="m" style="background:#0f6f63"></span>Dato de 1 hora</span>
<span><span class="m" style="background:#965806"></span>1 día</span>
<span><span class="m" style="background:#ae3b2f"></span>1 semana</span>
<span style="margin-left:auto">Claude y Codex · 11,9 millones de viajes</span></div>
</div></body></html>"""
    destino = RAIZ / "web" / "compartir.png"
    with tempfile.TemporaryDirectory() as tmp:
        html = Path(tmp) / "compartir.html"
        html.write_text(pagina, encoding="utf-8")
        subprocess.run([str(navegador()), "--headless=new", "--disable-gpu", "--hide-scrollbars",
                        "--force-device-scale-factor=1", "--window-size=1200,630", f"--user-data-dir={tmp}",
                        "--virtual-time-budget=5000", f"--screenshot={destino}", html.as_uri()],
                       check=True, capture_output=True, timeout=120)
    print(f"{destino.relative_to(RAIZ)}: {destino.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
