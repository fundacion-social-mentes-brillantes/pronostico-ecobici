"""La página web no puede quedar desactualizada: sus cifras salen de los resultados guardados."""
import json
import re
from html.parser import HTMLParser

from src import config, exportar_web

WEB = config.RAIZ / "web"


def datos_publicados():
    texto = (WEB / "datos.js").read_text(encoding="utf-8")
    return json.loads(texto[texto.index("{"):texto.rindex("}") + 1])


def formato(x, dec):
    """El mismo formato que app.js: punto de miles, coma decimal."""
    entero, _, fraccion = f"{abs(x):.{dec}f}".partition(".")
    entero = re.sub(r"\B(?=(\d{3})+(?!\d))", ".", entero)
    return ("−" if x < 0 else "") + entero + ("," + fraccion if fraccion else "")


class Cifras(HTMLParser):
    """Junta los elementos con data-cifra y el texto que traen escrito (el que se ve sin JavaScript)."""

    def __init__(self):
        super().__init__()
        self.pila = []
        self.cifras = []

    def handle_starttag(self, etiqueta, atributos):
        atributos = dict(atributos)
        self.pila.append([etiqueta, atributos.get("data-cifra"), int(atributos.get("data-dec") or 0), ""])

    def handle_endtag(self, etiqueta):
        while self.pila:
            e, ruta, dec, texto = self.pila.pop()
            if self.pila:
                self.pila[-1][3] += texto
            if ruta:
                self.cifras.append((ruta, dec, texto.strip()))
            if e == etiqueta:
                break

    def handle_data(self, datos):
        if self.pila:
            self.pila[-1][3] += datos


def valor(datos, ruta):
    for clave in ruta.split("."):
        datos = len(datos) if clave == "length" else datos[clave]
    return datos


def test_datos_js_coincide_con_los_resultados():
    publicado = datos_publicados()
    nuevo = {"retrasos": config.RETRASOS, "semanas": exportar_web.semanas(), "metricas": exportar_web.metricas(),
             "contrastes": exportar_web.contrastes(), "cifras": exportar_web.cifras(),
             "particiones": exportar_web.particiones()}
    nuevo = json.loads(json.dumps(nuevo, ensure_ascii=False))  # mismas claves de texto que el archivo publicado
    for clave, contenido in nuevo.items():
        assert publicado[clave] == contenido, f"web/datos.js está desactualizado en «{clave}»: corre src/exportar_web.py"


def test_las_cifras_escritas_en_la_pagina_coinciden_con_los_datos():
    lector = Cifras()
    lector.feed((WEB / "index.html").read_text(encoding="utf-8"))
    datos = datos_publicados()
    assert len(lector.cifras) >= 30  # hoy son 39
    for ruta, dec, escrito in lector.cifras:
        assert escrito == formato(valor(datos, ruta), dec), f"{ruta}: la página dice «{escrito}»"


def test_la_semana_inicial_es_la_mas_parecida_al_semestre():
    s = datos_publicados()["semanas"]
    tipica = s["lista"][s["tipica"]]
    assert tipica["horas_validas"] >= 160
    assert s["error_crece_en"] <= len(s["lista"])
