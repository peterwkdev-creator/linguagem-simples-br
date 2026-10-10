"""Leitura de HTML: texto em blocos e posição de cada trecho no arquivo."""

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from linguagem_simples.__main__ import main
from linguagem_simples.pagina import decodificar, ler_html, parece_html
from linguagem_simples.relatorio import como_dict, como_texto, conferir
from linguagem_simples.texto import ITEM, PARAGRAFO, TITULO, blocos


def tipos(html):
    texto = ler_html(html).texto
    return [(b.tipo, b.em(texto)) for b in blocos(texto)]


class TestTexto(unittest.TestCase):
    def test_blocos_itens_e_titulos(self):
        html = ("<h2>Como pedir</h2><p>Leve o documento.</p>"
                "<ul><li>RG.</li><li><p>CPF.</p></li></ul><table><tr><td>Sim</td><td>Não</td></tr></table>")
        self.assertEqual(tipos(html), [
            (TITULO, "Como pedir"), (PARAGRAFO, "Leve o documento."),
            (ITEM, "RG."), (ITEM, "CPF."), (PARAGRAFO, "Sim"), (PARAGRAFO, "Não"),
        ])

    def test_paragrafo_sem_fechar(self):
        self.assertEqual(ler_html("<p>Um.<p>Dois.").texto, "Um.\n\nDois.")

    def test_bloco_fecha_no_fim_da_tag(self):
        for html in ("<p>Um.</p>Dois.", "<p>Um.</p><br>Dois.", "<p>Um.</p><p> Dois.</p>", "<hr hidden><p>Um.</p>Dois."):
            with self.subTest(html):
                self.assertEqual(ler_html(html).texto, "Um.\n\nDois.")

    def test_espaco_e_quebra_de_linha(self):
        self.assertEqual(ler_html("<p>  Leve   o\r\n  RG <br> ao posto. </p>").texto, "Leve o RG\nao posto.")

    def test_entidades(self):
        self.assertEqual(ler_html("<p>Sa&uacute;de &amp; vida&nbsp;boa &#233; &#xE9;</p>").texto,
                         "Saúde & vida boa é é")

    def test_o_que_nao_e_texto_da_pagina(self):
        html = ("<!DOCTYPE html><html><head><title>Título</title><style>p{}</style></head><body>"
                "<nav><ul><li>Menu<p>sem fechar</nav><script>var p = '<p>';</script>"
                "<div hidden><div>oculto</div>ainda oculto</div><select><option>Opção</select>"
                "<!-- comentário --><p>Texto.</p></body></html>")
        self.assertEqual(ler_html(html).texto, "Texto.")

    def test_so_o_main_quando_existe(self):
        html = "<header><p>Portal</p></header><main><p>Conteúdo.</p></main><footer><p>Rodapé</p></footer>"
        self.assertEqual(ler_html(html).texto, "Conteúdo.")
        self.assertEqual(ler_html(html.replace("main>", "div>")).texto, "Portal\n\nConteúdo.\n\nRodapé")


class TestPosicao(unittest.TestCase):
    HTML = ("<!DOCTYPE html>\r\n<html><body>\r\n<h1>Sa&uacute;de</h1>\r\n"
            "<p>Leve  o RG<br>ao INSS&nbsp;hoje.</p>\r\n</body></html>")

    def test_cada_caractere_aponta_para_o_html(self):
        p = ler_html(self.HTML)
        for i, c in enumerate(p.texto):
            original = self.HTML[p.inicios[i]:p.fins[i]]
            if c in "\n#- ":  # quebra, marca e espaço vêm de tag ou de espaço do HTML
                continue
            with self.subTest(c=c):
                self.assertIn(original, (c, "&uacute;"))

    def test_trecho_no_html(self):
        p = ler_html(self.HTML)
        i = p.texto.index("INSS")
        a, b = p.na_fonte(i, i + 4)
        self.assertEqual(self.HTML[a:b], "INSS")
        i = p.texto.index("Saúde")
        a, b = p.na_fonte(i, i + 5)
        self.assertEqual(self.HTML[a:b], "Sa&uacute;de")
        a, b = p.na_fonte(i, i + 3)
        self.assertEqual(self.HTML[a:b], "Sa&uacute;")
        self.assertEqual(p.na_fonte(len(p.texto), len(p.texto)), (len(self.HTML), len(self.HTML)))

    def test_relatorio_da_linha_e_coluna_do_html(self):
        p = ler_html(self.HTML)
        resultados = conferir(p.texto)
        viii = next(i for i in como_dict(resultados, p)["incisos"] if i["inciso"] == "VIII")
        o = viii["ocorrencias"][0]
        self.assertEqual((o["trecho"], o["linha"], o["coluna"]), ("RG", 4, 12))
        self.assertEqual(self.HTML[o["inicio"]:o["fim"]], "RG")
        self.assertIn("linha 4, coluna 12: RG", como_texto(resultados, p))


class TestElementos(unittest.TestCase):
    HTML = ('<header><a href="/">Início</a></header><main>\r\n<p>Veja <a href="e.pdf" title="Edital">o '
            '<b>edital</b> <img src="i.png" alt="em PDF"></a>.</p>\r\n<img src="m.png">'
            "<table><tr><th>A</th></tr></table><a name=\"x\">âncora</a></main>")

    def test_links_imagens_e_tabelas_do_main(self):
        p = ler_html(self.HTML)
        self.assertEqual([e.tag for e in p.elementos], ["a", "img", "img", "table"])
        link, dentro, solta, tabela = p.elementos
        self.assertEqual(link.texto, "o edital em PDF")
        self.assertEqual(self.HTML[link.inicio:link.fim], self.HTML[self.HTML.index('<a href="e'):self.HTML.index(".</p>")])
        self.assertEqual((link.atributo("title"), link.atributo("alt")), ("Edital", None))
        self.assertEqual(self.HTML[solta.inicio:solta.fim], '<img src="m.png">')
        self.assertTrue(tabela.cabecalho)
        self.assertEqual(self.HTML[tabela.fim - 8:tabela.fim], "</table>")
        self.assertEqual(ler_html('<img src="a" alt>').elementos[0].atributo("alt"), "")
        # a marca do título e a quebra de linha não entram no texto do link
        self.assertEqual(ler_html('<a href="x"><h3>Saiba\n  mais</h3></a>').elementos[0].texto, "Saiba mais")

    def test_sem_main_vale_a_pagina_toda(self):
        self.assertEqual(len(ler_html(self.HTML.replace("main>", "div>")).elementos), 5)

    def test_no_texto(self):
        p = ler_html(self.HTML)
        link = p.elementos[0]
        inicio, fim = p.no_texto(link.inicio, link.fim)
        self.assertEqual(p.texto[inicio:fim], "o edital ")  # o alt não é texto da página
        self.assertEqual(p.no_texto(0, 0), (0, 0))

    def test_relatorio_aponta_a_tag_no_html(self):
        p = ler_html(self.HTML.replace('>o <b>edital</b> <img src="i.png" alt="em PDF">', ">aqui"))
        xvii = next(i for i in como_dict(conferir(p), p)["incisos"] if i["inciso"] == "XVII")
        self.assertEqual(xvii["estado"], "conferido")
        self.assertEqual([(o["trecho"], o["linha"], o["coluna"]) for o in xvii["ocorrencias"]],
                         [("aqui", 2, 9), ('<img src="m.png">', 3, 1)])
        o = xvii["ocorrencias"][1]
        self.assertEqual(p.fonte[o["inicio"]:o["fim"]], '<img src="m.png">')
        self.assertIn('linha 3, coluna 1: imagem sem texto alternativo', como_texto(conferir(p), p))
        # o texto sozinho só tem os links em Markdown
        self.assertEqual(next(r for r in conferir(p.texto) if r.inciso.numero == "XVII").ocorrencias, ())


class TestBytes(unittest.TestCase):
    def test_utf8_com_e_sem_bom(self):
        self.assertEqual(decodificar("<p>ação</p>".encode("utf-8")), "<p>ação</p>")
        self.assertEqual(decodificar("﻿<p>ação</p>".encode("utf-8")), "<p>ação</p>")

    def test_charset_declarado(self):
        dados = '<meta charset="iso-8859-1"><p>ação</p>'.encode("latin-1")
        self.assertEqual(decodificar(dados), '<meta charset="iso-8859-1"><p>ação</p>')
        dados = '<meta http-equiv="Content-Type" content="text/html; charset=windows-1252"><p>ação</p>'.encode("cp1252")
        self.assertTrue(decodificar(dados).endswith("<p>ação</p>"))

    def test_sem_charset_ou_desconhecido(self):
        with self.assertRaises(UnicodeDecodeError):
            decodificar("<p>ação</p>".encode("latin-1"))
        with self.assertRaises(LookupError):
            decodificar('<meta charset="nao-existe"><p>ação</p>'.encode("latin-1"))

    def test_parece_html(self):
        for dados in (b"<!DOCTYPE html><p>", b"\xef\xbb\xbf\n <html lang='pt'>", b"<!doctype HTML>"):
            self.assertTrue(parece_html(dados), dados)
        for dados in (b"Texto <html> no meio", b"<htmlx>", b"# Titulo"):
            self.assertFalse(parece_html(dados), dados)


class TestLinhaDeComando(unittest.TestCase):
    def rodar(self, nome, dados, *args):
        saida = io.StringIO()
        with tempfile.TemporaryDirectory() as pasta:
            arquivo = Path(pasta) / nome
            arquivo.write_bytes(dados)
            with contextlib.redirect_stdout(saida):
                codigo = main(["--json", *args, str(arquivo)])
        viii = next(i for i in json.loads(saida.getvalue())["incisos"] if i["inciso"] == "VIII")
        return codigo, [(o["trecho"], o["linha"], o["coluna"]) for o in viii["ocorrencias"]]

    # Lida como texto, a tag <DIV> vira mais uma sigla; lida como HTML, some.
    DIV = b"<DIV>\nLeve ao INSS.</DIV>"

    def test_html_pela_extensao_pelo_conteudo_e_pela_opcao(self):
        esperado = (1, [("INSS", 2, 9)])
        self.assertEqual(self.rodar("pagina.HTM", self.DIV), esperado)
        self.assertEqual(self.rodar("pagina.txt", self.DIV, "--html"), esperado)
        self.assertEqual(self.rodar("pagina.txt", b"<!DOCTYPE html>" + self.DIV), esperado)

    def test_texto_continua_texto(self):
        self.assertEqual(self.rodar("nota.txt", self.DIV), (1, [("DIV", 1, 2), ("INSS", 2, 9)]))

    def test_xvii_so_lendo_como_html(self):
        dados = '<p>Formulário: <a href="f.pdf">clique aqui</a></p><img src="a.png">'.encode()
        saida = io.StringIO()
        with tempfile.TemporaryDirectory() as pasta:
            for nome, esperado in (("p.html", ["link", "imagem"]), ("p.txt", [])):
                arquivo = Path(pasta) / nome
                arquivo.write_bytes(dados)
                with contextlib.redirect_stdout(saida):
                    main(["--json", str(arquivo)])
                d = json.loads(saida.getvalue())
                saida.seek(0), saida.truncate()
                xvii = next(i for i in d["incisos"] if i["inciso"] == "XVII")
                with self.subTest(nome):
                    self.assertEqual([o["mensagem"].split()[0] for o in xvii["ocorrencias"]], esperado)

    def test_charset_desconhecido_sai_com_2(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as fim:
            self.rodar("p.html", '<meta charset="nao-existe"><p>ação</p>'.encode("latin-1"))
        self.assertEqual(fim.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
