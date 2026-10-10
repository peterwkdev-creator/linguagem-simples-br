"""Vitrine: HTML colado no campo se lê como página, e o XVII aparece.

O `test_vitrine.py` é cópia do modelo da Coordenação e não se edita; o que
é só deste adaptador fica aqui.
"""
import importlib.util
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("montar", RAIZ / "vitrine" / "montar.py")
montar = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(montar)
executar = montar.carregar_adaptador(RAIZ).executar


def marcas(texto):
    res = executar({"texto": texto})
    # a página só desenha marca que cai dentro do campo
    assert montar.conferir_resultado(res, {"texto": texto}, "texto") == [], res
    return [(texto[m["inicio"]:m["fim"]], m["rotulo"]) for m in res["marcas"]]


class TestVitrineHtml(unittest.TestCase):

    def test_html_colado_marca_a_tag_no_campo(self):
        html = ('  <main><p>Para pedir, <a href="/pedir">clique aqui</a>.</p>'
                '<img src="mapa.png"></main>')
        self.assertEqual(marcas(html), [
            ('<a href="/pedir">clique aqui</a>', "Inciso XVII"),
            ('<img src="mapa.png">', "Inciso XVII"),
        ])

    def test_trecho_do_texto_cai_no_html(self):
        html = "<p>Procure o <b>INSS</b>.</p>"
        self.assertEqual(marcas(html), [("INSS", "Inciso VIII")])

    def test_texto_comum_segue_como_texto(self):
        # sem a tag no começo, "clique aqui" é só texto: o XVII não confere
        self.assertEqual(marcas("Para pedir, clique aqui. Procure o INSS."), [("INSS", "Inciso VIII")])
        self.assertEqual(marcas("Veja [clique aqui](https://exemplo.gov.br)."),
                         [("[clique aqui](https://exemplo.gov.br)", "Inciso XVII")])

    def test_comeca_por_menor_que_sem_ser_tag(self):
        self.assertEqual(marcas("<3 Procure o INSS."), [("INSS", "Inciso VIII")])


if __name__ == "__main__":
    unittest.main()
