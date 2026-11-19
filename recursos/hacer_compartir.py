"""Genera web/compartir.jpg (1200 × 630), la imagen que muestran WhatsApp y las redes al compartir el enlace.

Estilo «Ciudad de noche», como la web: la ilustración de portada (web/img/portada-1672.webp, generada con IA por
Codex), el titular en Newsreader y las tres edades del dato. Se dibuja con Edge o Chrome sin ventana.
Uso: .venv/Scripts/python recursos/hacer_compartir.py
"""
import base64
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "memoria"))
from construir_pdf import navegador  # noqa: E402


def datos(ruta, tipo):
    return f"data:{tipo};base64," + base64.b64encode((RAIZ / ruta).read_bytes()).decode()


def main():
    pagina = f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><style>
@font-face {{ font-family: N; src: url({datos("web/fuentes/Newsreader-VF.woff2", "font/woff2")}) format("woff2"); font-weight: 200 800; }}
@font-face {{ font-family: S; src: url({datos("web/fuentes/SchibstedGrotesk-VF.woff2", "font/woff2")}) format("woff2"); font-weight: 400 900; }}
html, body {{ margin: 0; width: 1200px; height: 630px; overflow: hidden; background: #0b0f14; color: #ede9e1; }}
.fondo {{ position: absolute; inset: 0; background: url({datos("web/img/portada-1672.webp", "image/webp")}) 78% 50% / cover; }}
.fondo::after {{ content: ""; position: absolute; inset: 0;
  background: linear-gradient(90deg, #0b0f14 0%, rgb(11 15 20 / 0.88) 36%, rgb(11 15 20 / 0.1) 75%); }}
.caja {{ position: relative; box-sizing: border-box; width: 1200px; height: 630px; padding: 70px 64px 56px;
  display: flex; flex-direction: column; }}
h1 {{ margin: 0; font-family: N; font-weight: 520; font-size: 68px; line-height: 1.02; letter-spacing: -0.02em;
  max-width: 640px; color: #f6f2ea; text-wrap: balance; }}
p {{ margin: 22px 0 0; font-family: S; font-size: 23px; line-height: 1.38; color: #c9ced6; max-width: 560px; }}
.pie {{ margin-top: auto; font-family: S; font-size: 18px; color: #b4bbc5; display: flex; gap: 22px; align-items: center; }}
.m {{ display: inline-block; width: 30px; height: 4px; border-radius: 2px; margin-right: 9px; vertical-align: middle; }}
</style></head><body><div class="fondo"></div><div class="caja">
<h1>El dato fresco pesa más que el modelo.</h1>
<p>Pronóstico de viajes de Ecobici, en Buenos Aires, con el último conteo de hace una hora, un día o una semana.</p>
<div class="pie"><span><span class="m" style="background:#3dd6c0"></span>dato de 1 hora</span>
<span><span class="m" style="background:#f5b54a"></span>1 día</span>
<span><span class="m" style="background:#ff7a66"></span>1 semana</span></div>
</div></body></html>"""
    destino = RAIZ / "web" / "compartir.jpg"
    with tempfile.TemporaryDirectory() as tmp:
        captura = Path(tmp) / "compartir.png"
        html = Path(tmp) / "compartir.html"
        html.write_text(pagina, encoding="utf-8")
        subprocess.run([str(navegador()), "--headless=new", "--disable-gpu", "--hide-scrollbars",
                        "--force-device-scale-factor=1", "--window-size=1200,630", f"--user-data-dir={tmp}",
                        "--virtual-time-budget=5000", f"--screenshot={captura}", html.as_uri()],
                       check=True, capture_output=True, timeout=120)
        # JPEG liviano: WhatsApp puede no mostrar vistas previas de más de unos 300 KB.
        from PIL import Image
        Image.open(captura).convert("RGB").save(destino, "JPEG", quality=84, optimize=True, progressive=True)
    print(f"{destino.relative_to(RAIZ)}: {destino.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
