"""Prepara las dos familias tipográficas del proyecto (ambas con licencia SIL Open Font License 1.1).

- Newsreader (Production Type): titulares y texto de lectura.
- Schibsted Grotesk (Schibsted): interfaz, etiquetas, tablas y figuras (tiene cifras tabulares).

Entrada: una carpeta con las versiones variables publicadas en Google Fonts
(Newsreader-VF.ttf, Newsreader-Italic-VF.ttf, SchibstedGrotesk-VF.ttf, más los OFL.txt de cada una).
Salidas:
- web/fuentes/*.woff2: variables, recortadas a los caracteres del español y la tipografía usada (para la web
  y el PDF de la memoria);
- recursos/fuentes/*.ttf: instancias fijas (regular y seminegrita) para las figuras de matplotlib.

Uso: python recursos/preparar_fuentes.py <carpeta con newsreader/ y schibstedgrotesk/>
Requiere fonttools y brotli (pip install fonttools brotli). Solo se corre una vez; los resultados están en el repo.
"""
import shutil
import sys
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

RAIZ = Path(__file__).resolve().parents[1]
WEB = RAIZ / "web" / "fuentes"
FIJAS = RAIZ / "recursos" / "fuentes"

# Latín básico y Latin-1 (tildes, ñ, ¿¡, «», ×, ·), comillas y rayas tipográficas, signo menos, flechas, ≈ ≤ ≥,
# espacios finos y la letra griega α (parámetro de regularización en las tablas).
# Más Latín extendido A (ŷ), acentos combinantes, cifras voladas y los símbolos de las fórmulas (∑, √) cuando la letra
# los tiene; lo que una letra no trae lo pone el navegador con otra.
CARACTERES = ("U+0020-007E,U+00A0-00FF,U+0100-017F,U+0300-0304,U+03B1,U+0394,U+2009,U+200A,U+2011,U+2013-2014,"
              "U+2018-201E,U+2022,U+2026,U+202F,U+2032-2033,U+2039-203A,U+2070-2079,U+20AC,U+2190-2193,U+2211,U+2212,"
              "U+221A,U+2248,U+2264-2265")


def recortar(fuente, destino, sabor):
    opciones = subset.Options()
    opciones.layout_features = ["*"]  # conserva cifras tabulares, versalitas de cifras, ligaduras, etc.
    opciones.flavor = sabor
    opciones.name_IDs = ["*"]
    opciones.notdef_outline = True
    recortador = subset.Subsetter(opciones)
    recortador.populate(unicodes=subset.parse_unicodes(CARACTERES))
    recortador.subset(fuente)
    fuente.flavor = sabor
    fuente.save(destino)


def main(origen):
    origen = Path(origen)
    WEB.mkdir(parents=True, exist_ok=True)
    FIJAS.mkdir(parents=True, exist_ok=True)
    variables = {
        "newsreader/Newsreader-VF.ttf": "Newsreader-VF.woff2",
        "newsreader/Newsreader-Italic-VF.ttf": "Newsreader-Italic-VF.woff2",
        "schibstedgrotesk/SchibstedGrotesk-VF.ttf": "SchibstedGrotesk-VF.woff2",
    }
    for entrada, salida in variables.items():
        recortar(TTFont(origen / entrada), WEB / salida, "woff2")
    for pesos, nombre in ((400, "Regular"), (600, "SemiBold")):
        fija = instancer.instantiateVariableFont(TTFont(origen / "schibstedgrotesk/SchibstedGrotesk-VF.ttf"),
                                                 {"wght": pesos}, updateFontNames=True)
        recortar(fija, FIJAS / f"SchibstedGrotesk-{nombre}.ttf", None)
    for familia, carpeta in (("Newsreader", "newsreader"), ("SchibstedGrotesk", "schibstedgrotesk")):
        for destino in (WEB, FIJAS):
            shutil.copy(origen / carpeta / "OFL.txt", destino / f"OFL-{familia}.txt")
    for ruta in sorted([*WEB.iterdir(), *FIJAS.iterdir()]):
        print(f"{ruta.relative_to(RAIZ)}  {ruta.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main(sys.argv[1])
