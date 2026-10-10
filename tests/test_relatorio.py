"""Relatório dos 18 incisos e linha de comando."""

import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from linguagem_simples.__main__ import main
from linguagem_simples.relatorio import (
    AVISO, CONFERIDO, DESLIGADO, NAO_CONFERIDO, SEM_DETECTOR,
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
        self.assertEqual([e["XV"], e["XVI"]], [SEM_DETECTOR] * 2)

    def test_xiii_e_sinal_e_roda(self):
        # 31% de precisão (amostra 6): o XIII aponta para quem lê decidir.
        texto = "O documento, que deve ser apresentado pelo requerente, fica no protocolo."
        por = {r.inciso.numero: r for r in conferir(texto)}
        self.assertEqual((por["XIII"].inciso.classe, por["XIII"].estado), ("sinal", CONFERIDO))
        self.assertEqual(len(por["XIII"].ocorrencias), 1)
        self.assertEqual([por[n].inciso.classe for n in ("II", "XII", "XIV")], ["automático"] * 3)
        self.assertIn("sinal; ", como_texto(conferir(texto), texto).split("XIII. ")[1].splitlines()[1])

    def test_ligar_e_desligar(self):
        e = estados(conferir(LONGA, ligar=["xi"], desligar=["II"]))
        self.assertEqual(e["XI"], SEM_DETECTOR)
        self.assertEqual(e["II"], DESLIGADO)
        self.assertEqual(sum(len(r.ocorrencias) for r in conferir(LONGA, desligar=["II"])), 0)

    def test_inciso_desconhecido(self):
        with self.assertRaises(ValueError):
            conferir("Texto.", ligar=["XIX"])

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


if __name__ == "__main__":
    unittest.main()
