"""Reescrita por IA: o aceite medido pelo verificador, com uma IA simulada
(nenhum teste usa a rede nem uma chave de verdade)."""

import contextlib
import io
import json
import os
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest import mock

from linguagem_simples import reescrita
from linguagem_simples.__main__ import main
from linguagem_simples.pagina import ler_html
from linguagem_simples.reescrita import ErroDeReescrita, _problemas, fatos, reescrever

# IV (deferido), VIII (INSS sem o nome) e XII (voz passiva): 3 apontamentos.
ORIGINAL = (
    "O pedido foi deferido em 15/10/2026 pelo INSS. Veja em https://www.gov.br/inss "
    "ou escreva para atendimento@inss.gov.br."
)
BOM = (
    "O Instituto Nacional do Seguro Social (INSS) aprovou o seu pedido em 15/10/2026. "
    "Veja em https://www.gov.br/inss ou escreva para atendimento@inss.gov.br."
)
SEM_DATA = BOM.replace(" em 15/10/2026", "")


class IA:
    """Responde, em ordem, o que recebeu e guarda cada pedido."""

    def __init__(self, *respostas):
        self.respostas = list(respostas)
        self.pedidos = []

    def __call__(self, sistema, mensagens):
        self.pedidos.append((sistema, [dict(m) for m in mensagens]))
        return self.respostas.pop(0)


def em_tags(texto):
    return f"<texto>\n{texto}\n</texto>"


class TestAceite(unittest.TestCase):
    def test_aceita_quando_cai_e_nada_some(self):
        ia = IA(em_tags(BOM))
        r = reescrever(ORIGINAL, chamar=ia)
        self.assertTrue(r.aceita)
        self.assertEqual((r.texto, r.tentativas, r.motivo), (BOM, 1, ""))
        self.assertEqual((r.total_antes, r.total_depois), (3, 0))
        sistema, mensagens = ia.pedidos[0]
        self.assertIn("Lei nº 15.263/2025", sistema)
        self.assertIn(ORIGINAL, mensagens[0]["content"])
        self.assertIn("deferido", mensagens[0]["content"])  # os apontamentos vão junto

    def test_tenta_de_novo_dizendo_o_que_sumiu(self):
        ia = IA(em_tags(SEM_DATA), em_tags(BOM))
        r = reescrever(ORIGINAL, chamar=ia)
        self.assertTrue(r.aceita)
        self.assertEqual(r.tentativas, 2)
        mensagens = ia.pedidos[1][1]
        self.assertEqual([m["role"] for m in mensagens], ["user", "assistant", "user"])
        self.assertIn("sumiu do texto: 15/10/2026", mensagens[2]["content"])

    def test_recusa_depois_das_tentativas_e_nao_entrega_o_texto(self):
        ia = IA(*[em_tags(ORIGINAL)] * 3)
        r = reescrever(ORIGINAL, chamar=ia)
        self.assertFalse(r.aceita)
        self.assertEqual((r.texto, r.tentativas), ("", 3))
        self.assertIn("não caiu (3 → 3)", r.motivo)
        self.assertEqual(len(ia.pedidos), 3)
        # A 2ª e a 3ª tentativa recebem o que o verificador ainda aponta.
        self.assertIn("ainda aponta", ia.pedidos[1][1][-1]["content"])

    def test_resposta_sem_tags_nao_conta_como_texto(self):
        r = reescrever(ORIGINAL, chamar=IA(BOM, BOM, BOM))
        self.assertFalse(r.aceita)
        self.assertIn("<texto>", r.motivo)

    def test_sem_apontamento_nao_chama_a_ia(self):
        ia = IA()
        r = reescrever(BOM, chamar=ia)
        self.assertFalse(r.aceita)
        self.assertEqual((r.tentativas, ia.pedidos), (0, []))
        self.assertIn("nada a reescrever", r.motivo)

    def test_opcoes_valem_no_antes_e_no_depois(self):
        # Com o VIII desligado, o original tem 2 apontamentos, não 3.
        r = reescrever(ORIGINAL, chamar=IA(em_tags(BOM)), desligar=["VIII"])
        self.assertEqual(r.total_antes, 2)
        self.assertNotIn("VIII", dict(r.antes))

    def test_pagina_reescreve_o_texto_dela(self):
        pagina = ler_html(f"<main><p>{ORIGINAL}</p></main>")
        ia = IA(em_tags(BOM))
        self.assertTrue(reescrever(pagina, chamar=ia).aceita)
        self.assertIn(ORIGINAL, ia.pedidos[0][1][0]["content"])
        self.assertNotIn("<main>", ia.pedidos[0][1][0]["content"])


class TestProblemas(unittest.TestCase):
    def test_inciso_que_piora_recusa_mesmo_com_o_total_menor(self):
        problemas = _problemas(BOM, BOM, (("II", 0), ("IV", 3)), (("II", 1), ("IV", 0)))
        self.assertEqual(problemas, ["o inciso II piorou (0 → 1)"])

    def test_numero_novo_recusa(self):
        novo = BOM + " O prazo é de 30 dias."
        self.assertEqual(_problemas(BOM, novo, (("IV", 1),), (("IV", 0),)),
                         ["número que o original não tem: 30"])

    def test_lista_numerada_nova_nao_e_numero_novo(self):
        novo = BOM + "\n\n1. Entre no site.\n2. Peça o serviço."
        self.assertEqual(_problemas(BOM, novo, (("IV", 1),), (("IV", 0),)), [])

    def test_link_email_e_sigla_que_somem_recusam(self):
        novo = "O instituto aprovou o seu pedido em 15/10/2026."
        problemas = _problemas(BOM, novo, (("IV", 1),), (("IV", 0),))
        self.assertEqual(problemas, ["sumiu do texto: https://www.gov.br/inss, atendimento@inss.gov.br, INSS"])


class TestFatos(unittest.TestCase):
    def test_o_que_conta_como_fato(self):
        self.assertEqual(fatos(ORIGINAL), ["https://www.gov.br/inss", "atendimento@inss.gov.br", "15/10/2026", "INSS"])
        self.assertEqual(fatos("Pague R$ 1.500,00 até 10/11 (art. 5º)."), ["1.500,00", "10/11", "5"])

    def test_titulo_em_caixa_alta_e_marca_de_lista_ficam_de_fora(self):
        self.assertEqual(fatos("ATENÇÃO\n\nPRAZO: 10 dias.\n\n1. Leve o RG.\n2. Leve o CPF."),
                         ["10", "PRAZO", "RG", "CPF"])

    def test_titulo_que_muda_de_caixa_nao_some(self):
        original = "PRAZO: 10 dias para o INSS responder."
        self.assertEqual(_problemas(original, "Prazo: 10 dias para o INSS responder.", (("XII", 1),), (("XII", 0),)), [])


class Resposta(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *erro):
        return False


def _resposta_da_api(texto, parada="end_turn"):
    corpo = {"content": [{"type": "text", "text": texto}], "stop_reason": parada}
    return Resposta(json.dumps(corpo).encode("utf-8"))


class TestChamada(unittest.TestCase):
    CHAVE = "chave-de-teste-nao-e-real"

    def test_requisicao_a_api(self):
        with mock.patch.dict(os.environ, {reescrita.VARIAVEL_DA_CHAVE: self.CHAVE}), \
                mock.patch("urllib.request.urlopen", return_value=_resposta_da_api(em_tags(BOM))) as urlopen:
            r = reescrever(ORIGINAL, modelo="modelo-x")
        self.assertTrue(r.aceita)
        pedido = urlopen.call_args.args[0]
        self.assertEqual(pedido.full_url, reescrita.URL)
        self.assertEqual(pedido.get_header("X-api-key"), self.CHAVE)
        self.assertEqual(pedido.get_header("Anthropic-version"), reescrita.VERSAO_DA_API)
        corpo = json.loads(pedido.data)
        self.assertEqual(corpo["model"], "modelo-x")
        self.assertEqual(corpo["messages"][0]["role"], "user")
        self.assertNotIn(self.CHAVE, pedido.data.decode("utf-8"))  # a chave só vai no cabeçalho

    def test_sem_chave_nao_chama_a_rede(self):
        with mock.patch.dict(os.environ, {reescrita.VARIAVEL_DA_CHAVE: ""}), \
                mock.patch("urllib.request.urlopen") as urlopen:
            with self.assertRaisesRegex(ErroDeReescrita, reescrita.VARIAVEL_DA_CHAVE):
                reescrever(ORIGINAL)
        urlopen.assert_not_called()

    def test_erro_da_api_diz_o_codigo_e_nao_a_chave(self):
        corpo = io.BytesIO(json.dumps({"error": {"message": "invalid x-api-key"}}).encode())
        erro = urllib.error.HTTPError(reescrita.URL, 401, "Unauthorized", {}, corpo)
        with mock.patch.dict(os.environ, {reescrita.VARIAVEL_DA_CHAVE: self.CHAVE}), \
                mock.patch("urllib.request.urlopen", side_effect=erro):
            with self.assertRaises(ErroDeReescrita) as pego:
                reescrever(ORIGINAL)
        self.assertIn("401: invalid x-api-key", str(pego.exception))
        self.assertNotIn(self.CHAVE, str(pego.exception))

    def test_resposta_cortada_vira_erro(self):
        with mock.patch.dict(os.environ, {reescrita.VARIAVEL_DA_CHAVE: self.CHAVE}), \
                mock.patch("urllib.request.urlopen", return_value=_resposta_da_api("<texto>O pe", "max_tokens")):
            with self.assertRaisesRegex(ErroDeReescrita, "longo demais"):
                reescrever(ORIGINAL)


class TestLinhaDeComando(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.arquivo = Path(self.tmp.name) / "texto.txt"
        self.arquivo.write_text(ORIGINAL, encoding="utf-8")

    def rodar(self, *args, respostas=(em_tags(BOM),)):
        saida, erro = io.StringIO(), io.StringIO()
        ia = IA(*respostas)
        with mock.patch.object(reescrita, "_chamar_claude", return_value=ia), \
                contextlib.redirect_stdout(saida), contextlib.redirect_stderr(erro):
            try:
                codigo = main(list(args))
            except SystemExit as fim:
                codigo = fim.code
        return codigo, saida.getvalue(), erro.getvalue()

    def test_aceita_mostra_o_antes_e_depois_e_o_texto(self):
        codigo, saida, _ = self.rodar(str(self.arquivo), "--reescrever")
        self.assertEqual(codigo, 0)
        self.assertIn("Aceita na tentativa 1. Apontamentos: 3 → 0.", saida)
        self.assertIn(reescrita.AVISO_SENTIDO, saida)
        self.assertIn("Não é parecer jurídico", saida)
        self.assertIn(BOM, saida)
        self.assertEqual(self.arquivo.read_text(encoding="utf-8"), ORIGINAL)  # o original fica como estava

    def test_saida_grava_o_texto_em_outro_arquivo(self):
        destino = Path(self.tmp.name) / "novo.txt"
        codigo, saida, _ = self.rodar(str(self.arquivo), "--reescrever", "--saida", str(destino))
        self.assertEqual(codigo, 0)
        self.assertEqual(destino.read_text(encoding="utf-8"), BOM + "\n")
        self.assertNotIn(BOM, saida)
        self.assertIn(f"gravado em {destino}", saida)

    def test_saida_nunca_e_o_arquivo_lido(self):
        codigo, _, erro = self.rodar(str(self.arquivo), "--reescrever", "--saida", str(self.arquivo))
        self.assertEqual(codigo, 2)
        self.assertIn("nunca grava por cima do original", erro)
        self.assertEqual(self.arquivo.read_text(encoding="utf-8"), ORIGINAL)

    def test_recusada_sai_com_1_e_sem_o_texto(self):
        codigo, saida, _ = self.rodar(str(self.arquivo), "--reescrever", respostas=[em_tags(SEM_DATA)] * 3)
        self.assertEqual(codigo, 1)
        self.assertIn("Recusada depois de 3 tentativas", saida)
        self.assertNotIn(SEM_DATA, saida)

    def test_json(self):
        codigo, saida, _ = self.rodar(str(self.arquivo), "--reescrever", "--json")
        dados = json.loads(saida)
        self.assertEqual(codigo, 0)
        self.assertEqual((dados["aceita"], dados["texto"], dados["apontamentos"]), (True, BOM, {"antes": 3, "depois": 0}))
        self.assertIn({"inciso": "IV", "antes": 1, "depois": 0}, dados["por_inciso"])
        self.assertEqual(dados["modelo"], reescrita.MODELO_PADRAO)

    def test_modelo_e_saida_so_com_reescrever(self):
        for extra in (["--modelo", "outro"], ["--saida", "x.txt"]):
            codigo, _, erro = self.rodar(str(self.arquivo), *extra)
            self.assertEqual(codigo, 2)
            self.assertIn("só valem com --reescrever", erro)

    def test_sem_chave_sai_com_2(self):
        saida, erro = io.StringIO(), io.StringIO()
        with mock.patch.dict(os.environ, {reescrita.VARIAVEL_DA_CHAVE: ""}), \
                contextlib.redirect_stdout(saida), contextlib.redirect_stderr(erro):
            codigo = main([str(self.arquivo), "--reescrever"])
        self.assertEqual(codigo, 2)
        self.assertIn(reescrita.VARIAVEL_DA_CHAVE, erro.getvalue())


if __name__ == "__main__":
    unittest.main()
