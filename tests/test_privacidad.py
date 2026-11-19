"""Los documentos que se publican no llevan datos personales en sus propiedades internas."""
import zipfile

import pytest

from src import config

PUBLICADOS = [config.RAIZ / "memoria" / "memoria.docx"]


@pytest.mark.parametrize("ruta", PUBLICADOS, ids=lambda r: r.name)
def test_el_word_no_guarda_quien_lo_modifico(ruta):
    # Word escribe en «modificado por» el nombre de quien lo guarda (por ejemplo, al actualizar el índice).
    propiedades = zipfile.ZipFile(ruta).read("docProps/core.xml").decode("utf-8")
    assert "<cp:lastModifiedBy></cp:lastModifiedBy>" in propiedades or "<cp:lastModifiedBy/>" in propiedades         or "lastModifiedBy" not in propiedades
