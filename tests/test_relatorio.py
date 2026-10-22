"""Relatório dos 18 incisos e linha de comando."""

import contextlib
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from linguagem_simples import __version__
from linguagem_simples.__main__ import VITRINE, main
from linguagem_simples.relatorio import (
    AVISO, CONFERIDO, DESLIGADO, LEGENDA, NAO_CONFERIDO, SEM_DETECTOR,
    como_dict, como_texto, conferir, linha_coluna,
)

from . import guias

RAIZ = Path(__file__).resolve().parent.parent
LONGA = "Palavra " + " ".join(["dita"] * 24) + "."  # 25 palavras


def estados(resultados):
    return {r.inciso.numero: r.estado for r in resultados}


def _sem_utf8_forcado():
    env = dict(os.environ)
    for nome in ("PYTHONIOENCODING", "PYTHONUTF8"):
        env.pop(nome, None)
    return env


class TestRelatorio(unittest.TestCase):
    def test_os_18_incisos_na_ordem_da_lei(self):
        numeros = [r.inciso.numero for r in conferir("Texto curto.")]
        self.assertEqual(len(numeros), 18)
        self.assertEqual(numeros[:3], ["I", "II", "III"])
        self.assertEqual(numeros[-1], "XVIII")

    def test_estado_de_cada_classe(self):
        e = estados(conferir("Texto curto."))
        self.assertEqual([e["II"], e["III"], e["VIII"]], [CONFERIDO] * 3)
        self.assertEqual([e["X"], e["XVIII"]], [NAO_CONFERIDO] * 2)
        self.assertEqual(e["XI"], DESLIGADO)
        self.assertEqual(e["I"], SEM_DETECTOR)
        self.assertEqual([e["XII"], e["XIII"], e["XIV"]], [CONFERIDO] * 3)
        self.assertEqual(e["XV"], CONFERIDO)
        self.assertEqual(e["XVI"], SEM_DETECTOR)

    def test_xvi_e_sinal_sem_detector(self):
        # Nenhum guia oficial dá lista de palavras imprecisas (10/10/2026).
        por = {r.inciso.numero: r for r in conferir("Será feito em breve.")}
        self.assertEqual((por["XVI"].inciso.classe, por["XVI"].estado), ("sinal", SEM_DETECTOR))

    def test_vi_e_sinal_e_roda(self):
        # A lei aceita a palavra estrangeira de uso corrente: quem lê decide.
        por = {r.inciso.numero: r for r in conferir("Faça o login no sistema.")}
        self.assertEqual((por["VI"].inciso.classe, por["VI"].estado), ("sinal", CONFERIDO))
        self.assertEqual([o.trecho for o in por["VI"].ocorrencias], ["login"])

    def test_iv_e_sinal_e_roda(self):
        # O TJRS (p. 31) diz que a palavra difícil depende de quem lê: quem lê decide.
        por = {r.inciso.numero: r for r in conferir("O pedido foi deferido.")}
        self.assertEqual((por["IV"].inciso.classe, por["IV"].estado), ("sinal", CONFERIDO))
        self.assertEqual([o.trecho for o in por["IV"].ocorrencias], ["deferido"])

    def test_v_e_sinal_e_roda(self):
        # A lei aceita o termo técnico explicado no próprio texto: quem lê decide.
        por = {r.inciso.numero: r for r in conferir("A sentença transitou em julgado.")}
        self.assertEqual((por["V"].inciso.classe, por["V"].estado), ("sinal", CONFERIDO))
        self.assertEqual([o.trecho for o in por["V"].ocorrencias], ["transitou em julgado"])

    def test_xiii_e_sinal_e_roda(self):
        # 31% de precisão (amostra 6): o XIII aponta para quem lê decidir.
        texto = "O documento, que deve ser apresentado pelo requerente, fica no protocolo."
        por = {r.inciso.numero: r for r in conferir(texto)}
        self.assertEqual((por["XIII"].inciso.classe, por["XIII"].estado), ("sinal", CONFERIDO))
        self.assertEqual(len(por["XIII"].ocorrencias), 1)
        self.assertEqual([por[n].inciso.classe for n in ("II", "XII", "XIV")], ["automático"] * 3)
        self.assertIn("sinal; ", como_texto(conferir(texto), texto).split("XIII. ")[1].splitlines()[1])

    def test_ix_e_sinal_e_roda_com_o_limiar(self):
        # A lei diz "quando couber": o IX aponta e quem lê decide.
        texto = "Leve ao atendimento os documentos: RG, CPF e comprovante de residência."
        por = {r.inciso.numero: r for r in conferir(texto)}
        self.assertEqual((por["IX"].inciso.classe, por["IX"].estado), ("sinal", CONFERIDO))
        self.assertEqual((len(por["IX"].ocorrencias), por["IX"].limiar), (1, 3))
        self.assertIn("SES-DF p. 6", por["IX"].fonte_do_limiar)

    def test_ligar_e_desligar(self):
        e = estados(conferir(LONGA, ligar=["xi"], desligar=["II"]))
        self.assertEqual(e["XI"], SEM_DETECTOR)
        self.assertEqual(e["II"], DESLIGADO)
        self.assertEqual(sum(len(r.ocorrencias) for r in conferir(LONGA, desligar=["II"])), 0)

    def test_inciso_desconhecido(self):
        with self.assertRaises(ValueError):
            conferir("Texto.", ligar=["XIX"])

    def test_limiar_menor_que_1(self):
        # a linha de comando já recusava; a biblioteca apontava toda frase
        for opcao in ({"max_palavras": 0}, {"max_frases": -1}):
            with self.subTest(opcao), self.assertRaises(ValueError):
                conferir(LONGA, **opcao)

    def test_ocorrencias_e_limiar(self):
        por = {r.inciso.numero: r for r in conferir("Procure o INSS.\n\n" + LONGA)}
        self.assertEqual([o.trecho for o in por["VIII"].ocorrencias], ["INSS"])
        self.assertEqual(len(por["II"].ocorrencias), 1)
        self.assertEqual(por["II"].limiar, 20)
        self.assertIn("TJGO", por["II"].fonte_do_limiar)
        por = {r.inciso.numero: r for r in conferir(LONGA, max_palavras=30)}
        self.assertEqual((por["II"].ocorrencias, por["II"].fonte_do_limiar), ((), "informado por quem usa"))

    def test_linha_e_coluna_com_crlf(self):
        texto = "Primeira.\r\n\r\nLeve ao INSS."
        self.assertEqual(linha_coluna(texto, texto.index("INSS")), (3, 9))
        self.assertEqual(linha_coluna(texto, 0), (1, 1))

    def test_texto_traz_aviso_os_18_e_a_posicao(self):
        texto = "Primeira frase.\n\nLeve ao INSS."
        saida = como_texto(conferir(texto), texto)
        self.assertIn(AVISO, saida)
        for numero in ("I.", "X.", "XI.", "XVIII."):
            self.assertIn("\n" + numero + " ", saida)
        self.assertIn("linha 3, coluna 9: INSS: primeira ocorrência", saida)
        self.assertIn("desligado por padrão", saida)
        self.assertIn("não conferido", saida)

    def test_resumo_e_legenda_no_topo(self):
        texto = "Leve ao INSS. Fale com o SUS."
        topo = como_texto(conferir(texto), texto).split("\n\nI. ")[0]
        self.assertIn("\nTrechos a revisar: 2 (VIII: 2), listados abaixo com linha e coluna.\n", topo)
        self.assertTrue(topo.endswith("\n" + LEGENDA), topo)
        self.assertIn("nenhuma ocorrência não garante", LEGENDA)
        limpo = "Texto curto."
        self.assertIn("\nNada a revisar nos incisos conferidos.\n", como_texto(conferir(limpo), limpo))

    def test_exemplo_do_readme_e_a_saida_real(self):
        readme = (RAIZ / "README.md").read_text(encoding="utf-8")
        uso = readme.split("\n## Uso\n")[1].split("\n### ")[0]
        texto = " ".join(re.search(r"o texto “(.+?)”, o relatório", uso, re.S).group(1).split())
        blocos = re.findall(r"```text\n(.*?)```", uso, re.S)
        saida = como_texto(conferir(texto), texto) + "\n"
        self.assertEqual(len(blocos), 3)
        self.assertTrue(saida.startswith(blocos[0]), blocos[0])
        for bloco in blocos[1:]:
            self.assertIn("\n\n" + bloco, saida)

    def test_trecho_longo_e_cortado(self):
        texto = " ".join(["palavra"] * 40) + "."
        saida = como_texto(conferir(texto), texto)
        self.assertIn("…”", saida)

    def test_json(self):
        texto = "Leve ao INSS."
        d = json.loads(json.dumps(como_dict(conferir(texto), texto), ensure_ascii=False))
        self.assertEqual(d["aviso"], AVISO)
        self.assertEqual(len(d["incisos"]), 18)
        viii = next(i for i in d["incisos"] if i["inciso"] == "VIII")
        self.assertEqual(viii["ocorrencias"][0]["inicio"], 8)
        self.assertEqual((viii["ocorrencias"][0]["linha"], viii["ocorrencias"][0]["coluna"]), (1, 9))
        x = next(i for i in d["incisos"] if i["inciso"] == "X")
        self.assertNotIn("ocorrencias", x)

    def test_texto_bom_do_guia(self):
        # Medido em 09/10/2026, com os padrões: o texto que o guia dá como
        # bom só aparece na voz passiva (XII) e, na Anvisa, que aceita até 25
        # palavras, numa frase de 23 (II).
        def achados(texto, **opcoes):
            return [(r.inciso.numero, o.trecho) for r in conferir(texto, **opcoes) for o in r.ocorrencias]

        self.assertEqual(achados(guias.FRASE_TJGO.depois), [])
        self.assertEqual(achados(guias.TREAL_PARAGRAFOS), [("XII", "ser utilizadas")])
        self.assertEqual(achados(guias.ANVISA_SEI_DEPOIS, max_palavras=25), [("XII", "ser punido")])
        self.assertEqual([n for n, _ in achados(guias.ANVISA_SEI_DEPOIS)], ["II", "XII"])

class TestLinhaDeComando(unittest.TestCase):
    def rodar(self, *args, entrada=None):
        saida = io.StringIO()
        with tempfile.TemporaryDirectory() as pasta:
            argv = list(args)
            if entrada is not None:
                arquivo = Path(pasta) / "texto.txt"
                arquivo.write_bytes(entrada.encode("utf-8"))
                argv.append(str(arquivo))
            with contextlib.redirect_stdout(saida):
                codigo = main(argv)
        return codigo, saida.getvalue()

    def test_codigo_de_saida(self):
        self.assertEqual(self.rodar(entrada="Texto curto.")[0], 0)
        self.assertEqual(self.rodar(entrada="Leve ao INSS.")[0], 1)
        self.assertEqual(self.rodar("--ignorar-sigla", "inss", entrada="Leve ao INSS.")[0], 0)

    def test_json_e_limiar(self):
        codigo, saida = self.rodar("--json", "--max-palavras", "30", entrada=LONGA)
        d = json.loads(saida)
        ii = next(i for i in d["incisos"] if i["inciso"] == "II")
        self.assertEqual((codigo, ii["limiar"], ii["ocorrencias"]), (0, 30, []))

    def test_arquivo_com_bom_do_bloco_de_notas(self):
        _, saida = self.rodar("--json", entrada="﻿Leve ao INSS.")
        viii = next(i for i in json.loads(saida)["incisos"] if i["inciso"] == "VIII")
        self.assertEqual(viii["ocorrencias"][0]["inicio"], 8)

    def test_versao(self):
        with contextlib.redirect_stdout(io.StringIO()) as saida, self.assertRaises(SystemExit) as fim:
            main(["--versao"])
        self.assertEqual((fim.exception.code, saida.getvalue()), (0, f"linguagem_simples {__version__}\n"))

    def test_nome_do_comando_instalado(self):
        # pelo pip, a ajuda e os erros dizem o comando que se digitou
        for argv0, nome in (("bin/linguagem-simples", "linguagem-simples"),
                            ("Scripts/linguagem-simples.exe", "linguagem-simples"),
                            ("linguagem_simples/__main__.py", "python -m linguagem_simples")):
            with self.subTest(argv0), mock.patch.object(sys, "argv", [argv0]), \
                    contextlib.redirect_stderr(io.StringIO()) as erro, self.assertRaises(SystemExit):
                main([])
            self.assertTrue(erro.getvalue().startswith(f"uso: {nome} arquivo [opções]\n"), erro.getvalue())
            self.assertIn(f"{nome}: erro: falta o arquivo a conferir. Exemplo: {nome} carta.txt", erro.getvalue())
            self.assertIn(VITRINE, erro.getvalue())

    def rodar_bytes(self, dados, *args, nome="texto.txt"):
        """A CLI num arquivo com estes bytes: código, saída e erro."""
        saida, erro = io.StringIO(), io.StringIO()
        with tempfile.TemporaryDirectory() as pasta, \
                contextlib.redirect_stdout(saida), contextlib.redirect_stderr(erro):
            arquivo = Path(pasta) / nome
            arquivo.write_bytes(dados)
            try:
                codigo = main([str(arquivo), *args])
            except SystemExit as fim:
                codigo = fim.code
        return codigo, saida.getvalue(), erro.getvalue()

    def test_entrada_padrao_no_terminal_explica_como_terminar(self):
        import linguagem_simples.__main__ as cli
        for terminal in (True, False):
            entrada = mock.Mock(buffer=io.BytesIO("Texto curto.".encode()))
            with self.subTest(terminal=terminal), mock.patch.object(sys, "stdin", entrada), \
                    mock.patch.object(cli, "_e_terminal", return_value=terminal), \
                    contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()) as erro:
                self.assertEqual(main(["-"]), 0)
            self.assertEqual("Ctrl+Z e Enter" in erro.getvalue(), terminal)

    def test_ajuda_em_portugues(self):
        with contextlib.redirect_stdout(io.StringIO()) as saida, self.assertRaises(SystemExit) as fim:
            main(["-h"])
        ajuda = saida.getvalue()
        self.assertEqual(fim.exception.code, 0)
        for trecho in ("uso: ", "\narquivo:\n", "\nopções:\n", "mostra esta ajuda e sai", "\nexemplos:\n",
                       "carta.txt --saida relatorio.txt\n", "código de saída: 0 nada a revisar", VITRINE):
            self.assertIn(trecho, ajuda)
        self.assertIn("hoje só o XI, que ainda não tem detector", " ".join(ajuda.split()))
        sem_link = ajuda.replace(VITRINE, "")
        self.assertLessEqual(max(len(linha) for linha in sem_link.splitlines()), 79)
        for ingles in ("usage:", "options:", "show this help", "positional arguments"):
            self.assertNotIn(ingles, ajuda)

    def test_erros_do_argparse_em_portugues(self):
        for args, esperado in ((["--max-palavras"], "--max-palavras precisa de um valor logo depois"),
                               (["--max-palavras", "abc"], "--max-palavras: use um número inteiro maior que zero"),
                               (["--max-frases", "0"], "--max-frases: use um número inteiro maior que zero"),
                               (["outro.txt"], "não entendi: outro.txt (um arquivo por vez"),
                               (["--json=sim"], "--json não leva valor"),
                               (["--max"], "--max é ambíguo: pode ser")):
            codigo, _, erro = self.rodar_bytes(b"Texto.", *args)
            with self.subTest(args):
                self.assertEqual(codigo, 2)
                self.assertIn(f": erro: {esperado}", erro)
                self.assertNotIn("error", erro)

    def test_documento_que_nao_e_texto(self):
        for dados, tipo in ((b"PK\x03\x04resto", "Word (.docx)"), (b"%PDF-1.7\n", "um PDF"),
                            (b"\xd0\xcf\x11\xe0\xa1\xb1", "Word antigo (.doc)"), (b"{\\rtf1\\ansi", "RTF")):
            codigo, saida, erro = self.rodar_bytes(dados, nome="documento.txt")
            with self.subTest(tipo):
                self.assertEqual((codigo, saida), (2, ""))
                self.assertIn(tipo, erro)
                self.assertIn("cole no Bloco de Notas e salve como .txt", erro)

    def test_arquivo_ansi_e_lido_com_aviso(self):
        codigo, saida, erro = self.rodar_bytes("Ação do INSS.".encode("cp1252"), "--max-palavras", "2")
        self.assertEqual(codigo, 1)
        self.assertIn("“Ação do INSS.”", saida)
        self.assertIn("aviso: ", erro)
        self.assertIn("lido como Windows-1252", erro)
        self.assertIn("Codificação: UTF-8", erro)
        # em UTF-8, nenhum aviso
        self.assertEqual(self.rodar_bytes("Ação do INSS.".encode("utf-8"))[2], "")

    def test_byte_que_nem_o_ansi_tem(self):
        codigo, _, erro = self.rodar_bytes(b"A\x81B \xe7")
        self.assertEqual(codigo, 2)
        self.assertIn("não está em UTF-8", erro)
        self.assertIn("Salvar como > Codificação: UTF-8", erro)

    def test_unicode_do_bloco_de_notas(self):
        for codificacao in ("utf-16", "utf-16-be"):
            dados = "﻿Leve ao INSS.".encode(codificacao)
            codigo, saida, erro = self.rodar_bytes(dados, "--json")
            with self.subTest(codificacao):
                viii = next(i for i in json.loads(saida)["incisos"] if i["inciso"] == "VIII")
                self.assertEqual((codigo, erro, [o["inicio"] for o in viii["ocorrencias"]]), (1, "", [8]))

    def test_arquivo_ou_pasta_que_nao_servem(self):
        with tempfile.TemporaryDirectory() as pasta, contextlib.redirect_stderr(io.StringIO()) as erro:
            for args in ([str(Path(pasta) / "nao-existe.txt")], [pasta]):
                with self.assertRaises(SystemExit) as fim:
                    main(args)
                self.assertEqual(fim.exception.code, 2)
        self.assertIn("não achei ", erro.getvalue())
        self.assertIn("'dir' lista os arquivos", erro.getvalue())
        self.assertIn("é uma pasta: indique um arquivo dentro dela", erro.getvalue())

    def test_saida_grava_o_relatorio(self):
        with tempfile.TemporaryDirectory() as pasta:
            destino = Path(pasta) / "relatorio.txt"
            codigo, saida, _ = self.rodar_bytes("Leve ao INSS.".encode(), "--saida", str(destino))
            self.assertEqual(codigo, 1)
            self.assertEqual(saida, f"Relatório gravado em {destino}. Trechos a revisar: 1 (VIII: 1), "
                             "listados abaixo com linha e coluna.\n")
            self.assertIn("INSS: primeira ocorrência", destino.read_text(encoding="utf-8"))
            # nunca por cima
            codigo, _, erro = self.rodar_bytes(b"Outro texto.", "--saida", str(destino))
            self.assertEqual(codigo, 2)
            self.assertIn("já existe", erro)
            self.assertIn("INSS", destino.read_text(encoding="utf-8"))
            em_json = Path(pasta) / "relatorio.json"
            self.assertEqual(self.rodar_bytes(b"Texto curto.", "--json", "--saida", str(em_json))[0], 0)
            self.assertEqual(len(json.loads(em_json.read_text(encoding="utf-8"))["incisos"]), 18)

    def test_defeito_do_verificador_sai_com_2_e_nao_com_1(self):
        # 1 quer dizer "achou ocorrências": um traceback não pode passar por isso
        import linguagem_simples.__main__ as cli
        saida, erro = (io.TextIOWrapper(io.BytesIO()) for _ in range(2))
        with mock.patch.object(cli, "main", side_effect=StopIteration), \
                mock.patch.object(sys, "stdout", saida), mock.patch.object(sys, "stderr", erro):
            codigo = cli.comando()
        erro.seek(0)
        self.assertEqual(codigo, 2)
        self.assertIn("erro inesperado (StopIteration); avise em https://github.com/", erro.read())

    def test_erros_de_uso_saem_com_2(self):
        erro = io.StringIO()
        with self.subTest("arquivo"), contextlib.redirect_stderr(erro), self.assertRaises(SystemExit) as fim:
            main(["nao-existe.txt"])
        self.assertEqual(fim.exception.code, 2)
        # Arquivo existente: o erro tem de vir da opção, não da leitura.
        for opcao in (["--max-palavras", "0"], ["--ligar", "XIX"]):
            with self.subTest(opcao), contextlib.redirect_stderr(erro), self.assertRaises(SystemExit) as fim:
                self.rodar(*opcao, entrada="Texto.")
            self.assertEqual(fim.exception.code, 2)

    def test_processo_de_verdade_com_saida_redirecionada(self):
        # Sem PYTHONIOENCODING: a saída redirecionada tem de sair em UTF-8.
        r = subprocess.run(
            [sys.executable, "-m", "linguagem_simples", "-"],
            input="Leve ao INSS. Atenção à sigla.".encode("utf-8"),
            cwd=RAIZ, capture_output=True, env=_sem_utf8_forcado(),
        )
        self.assertEqual(r.returncode, 1, r.stderr)
        saida = r.stdout.decode("utf-8")
        self.assertIn("INSS: primeira ocorrência sem o nome completo antes", saida)
        self.assertIn("relatório dos 18 incisos", saida)


class TestAuditoria(unittest.TestCase):
    """Linha e coluna sem recontar o texto, limiar novo, UTF-16 corrompido e
    caractere de controle na tela."""

    rodar_bytes = TestLinhaDeComando.rodar_bytes

    def test_linha_e_coluna_com_inicios_dao_o_mesmo(self):
        from linguagem_simples.relatorio import inicios_de_linha
        for texto in ("", "sem quebra", "a\nb\r\n\r\nc\n", "\n\nLeve ao INSS.\n"):
            inicios = inicios_de_linha(texto)
            for posicao in range(len(texto) + 1):
                with self.subTest(texto=texto, posicao=posicao):
                    self.assertEqual(linha_coluna(texto, posicao, inicios), linha_coluna(texto, posicao))

    def test_limiar_novo_nao_quebra_o_relatorio(self):
        from linguagem_simples import limiares
        with mock.patch.dict(limiares.LIMIARES, {"XII": limiares.Limiar(3, "guia de teste, p. 1")}):
            xii = next(r for r in conferir("O pedido foi feito.") if r.inciso.numero == "XII")
        self.assertEqual((xii.limiar, xii.fonte_do_limiar, len(xii.ocorrencias)), (3, "guia de teste, p. 1", 1))

    def test_utf16_corrompido_tem_mensagem_propria(self):
        codigo, _, erro = self.rodar_bytes(b"\xff\xfeO\x00l\x00\x00\xd8a\x00")
        self.assertEqual(codigo, 2)
        self.assertIn("começa como Unicode (UTF-16)", erro)
        self.assertNotIn("não está em UTF-8", erro)

    def test_controle_sai_so_da_tela(self):
        dados = "Texto com \x1b[2J e \x07 sino.\tFim aqui.".encode()
        codigo, saida, _ = self.rodar_bytes(dados, "--max-palavras", "2")
        self.assertEqual(codigo, 1)
        self.assertNotIn("\x1b", saida)
        self.assertNotIn("\x07", saida)
        self.assertIn("“Texto com [2J e  sino.”", saida)
        _, saida, _ = self.rodar_bytes(dados, "--max-palavras", "2", "--json")
        trechos = [o["trecho"] for i in json.loads(saida)["incisos"] for o in i.get("ocorrencias", ())]
        self.assertIn("Texto com \x1b[2J e \x07 sino.", trechos)
        with tempfile.TemporaryDirectory() as pasta:
            destino = Path(pasta) / "relatorio.txt"
            self.rodar_bytes(dados, "--max-palavras", "2", "--saida", str(destino))
            self.assertIn("\x1b[2J", destino.read_text(encoding="utf-8"))

    def test_marca_de_direcao_sai_so_da_tela(self):
        dados = "Texto com ‮odnum invertido aqui.".encode()
        _, saida, _ = self.rodar_bytes(dados, "--max-palavras", "2")
        self.assertNotIn("‮", saida)
        self.assertIn("“Texto com odnum invertido aqui.”", saida)
        _, saida, _ = self.rodar_bytes(dados, "--max-palavras", "2", "--json")
        self.assertIn("‮", json.loads(saida)["incisos"][1]["ocorrencias"][0]["trecho"])


if __name__ == "__main__":
    unittest.main()
