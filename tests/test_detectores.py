"""Duas provas por detector: pega o defeito plantado e não dispara no texto
que o guia oficial dá como bom. E, em cada par do guia, o "antes" conta mais
que o "depois"."""

import unittest
from pathlib import Path

from linguagem_simples import detectores, limiares
from linguagem_simples.detectores import (
    frases_intercaladas, frases_longas, paragrafos_longos, siglas_sem_nome,
    substantivos_no_lugar_de_verbos, voz_passiva,
)

from . import guias


def frase(n):
    """Frase plantada com exatamente ``n`` palavras."""
    return "Palavra " + " ".join(["dita"] * (n - 1)) + "."


class TestIncisoII(unittest.TestCase):
    def test_plantado_acima_do_limiar(self):
        achadas = frases_longas(frase(21) + " Curta.")
        self.assertEqual(len(achadas), 1)
        self.assertEqual((achadas[0].inciso, achadas[0].medida, achadas[0].inicio), ("II", 21, 0))

    def test_no_limiar_nao_dispara(self):
        self.assertEqual(frases_longas(frase(20)), [])

    def test_limiar_informado_vence_o_padrao(self):
        self.assertEqual(len(frases_longas(frase(6), max_palavras=5)), 1)

    def test_padrao_tem_fonte(self):
        self.assertEqual(limiares.LIMIARES["II"].padrao, 20)
        self.assertIn("TJGO", limiares.LIMIARES["II"].fonte)

    def test_texto_bom_do_guia_com_o_limiar_do_guia(self):
        for par in (guias.FRASE_TJGO, guias.FRASE_CAPES, guias.FRASE_ANVISA):
            with self.subTest(par.fonte.guia):
                self.assertEqual(frases_longas(par.depois, par.limiar_do_guia), [])

    def test_par_antes_conta_mais_com_o_limiar_do_guia(self):
        for par in (guias.FRASE_TJGO, guias.FRASE_CAPES, guias.FRASE_ANVISA):
            with self.subTest(par.fonte.guia):
                antes = frases_longas(par.antes, par.limiar_do_guia)
                depois = frases_longas(par.depois, par.limiar_do_guia)
                self.assertGreater(len(antes), len(depois))

    def test_com_o_padrao_de_20_capes_e_anvisa_empatam(self):
        # Medido em 09/10/2026: o "depois" da CAPES e o da Anvisa têm uma
        # frase de 21 palavras cada; os dois guias aceitam até 25. Com o
        # padrão de 20, cada par dá 1 a 1. O TJGO, que dá 20, fica 1 a 0.
        for par in (guias.FRASE_CAPES, guias.FRASE_ANVISA):
            with self.subTest(par.fonte.guia):
                self.assertEqual([o.medida for o in frases_longas(par.depois)], [21])
                self.assertEqual(len(frases_longas(par.antes)), 1)
        self.assertEqual(
            (len(frases_longas(guias.FRASE_TJGO.antes)), len(frases_longas(guias.FRASE_TJGO.depois))),
            (1, 0),
        )


class TestIncisoIII(unittest.TestCase):
    def test_plantado_acima_do_limiar(self):
        paragrafo = " ".join(frase(3) for _ in range(9))
        achadas = paragrafos_longos("Título curto.\n\n" + paragrafo)
        self.assertEqual(len(achadas), 1)
        self.assertEqual((achadas[0].inciso, achadas[0].medida), ("III", 9))
        self.assertEqual(achadas[0].trecho, paragrafo)

    def test_no_limiar_nao_dispara(self):
        self.assertEqual(paragrafos_longos(" ".join(frase(3) for _ in range(8))), [])

    def test_itens_de_lista_nao_sao_paragrafo(self):
        lista = "\n".join("- " + frase(3) for _ in range(9))
        self.assertEqual(paragrafos_longos(lista), [])
        item_comprido = "- " + " ".join(frase(3) for _ in range(9))
        self.assertEqual(paragrafos_longos(item_comprido), [])

    def test_padrao_tem_fonte(self):
        self.assertEqual(limiares.LIMIARES["III"].padrao, 8)
        self.assertIn("TRE-AL", limiares.LIMIARES["III"].fonte)

    def test_texto_bom_do_guia(self):
        self.assertEqual(paragrafos_longos(guias.TREAL_PARAGRAFOS), [])
        self.assertEqual(paragrafos_longos(guias.ANVISA_SEI_DEPOIS), [])


class TestIncisoVIII(unittest.TestCase):
    def siglas(self, texto):
        return [o.trecho for o in siglas_sem_nome(texto)]

    def test_plantado_sem_nome(self):
        achadas = siglas_sem_nome("Procure o INSS.")
        self.assertEqual(len(achadas), 1)
        self.assertEqual((achadas[0].inciso, achadas[0].inicio, achadas[0].fim), ("VIII", 10, 14))

    def test_plantado_com_nome_depois(self):
        achadas = siglas_sem_nome("Procure o INSS (Instituto Nacional do Seguro Social).")
        self.assertEqual(len(achadas), 1)
        self.assertIn("depois", achadas[0].mensagem)

    def test_nome_antes_e_depois_so_a_sigla(self):
        texto = "Procure o Instituto Nacional do Seguro Social (INSS). O INSS atende."
        self.assertEqual(self.siglas(texto), [])

    def test_sigla_usada_antes_de_ser_definida(self):
        texto = "Leve ao INSS. O Instituto Nacional do Seguro Social (INSS) atende."
        self.assertEqual(self.siglas(texto), ["INSS"])

    def test_nome_que_nao_corresponde_as_letras(self):
        self.assertEqual(self.siglas("Leve o documento (RG)."), ["RG"])
        achadas = siglas_sem_nome("Leve o RG (original e cópia).")
        self.assertIn("sem o nome completo antes", achadas[0].mensagem)

    def test_iniciais_em_ordem_com_palavras_no_meio(self):
        texto = (
            "A Secretaria Especial da Receita Federal do Brasil (RFB) e o "
            "Sistema Único de Saúde (SUS)."
        )
        self.assertEqual(self.siglas(texto), [])

    # Os casos a seguir vêm dos erros da amostra anotada (corpus/amostra.md,
    # 09/10/2026): o nome vinha antes, numa forma que o detector não via.
    def test_mais_de_uma_letra_da_mesma_palavra(self):
        self.assertEqual(self.siglas("Centro de Pesquisa em Medicina Tropical (CEPEM)."), [])
        self.assertEqual(self.siglas("Câmeras de circuito fechado de TV (CFTV)."), ["TV"])
        self.assertEqual(self.siglas("Centro de Medicina (CEPEM)."), ["CEPEM"])

    def test_palavra_antes_da_sigla_no_parentese(self):
        self.assertEqual(self.siglas("A curva de ponto de ebulição verdadeiro (curva PEV)."), [])
        self.assertEqual(self.siglas("O ponto de ebulição verdadeiro (a nova curva PEV)."), ["PEV"])
        self.assertEqual(self.siglas("O ponto de ebulição verdadeiro (PEV, em graus)."), ["PEV"])

    def test_nome_ligado_so_na_mesma_frase_e_perto(self):
        self.assertEqual(self.siglas("Fale com o Centro de Pesquisa. Em Medicina (CEPEM) atende."), ["CEPEM"])
        self.assertEqual(self.siglas("Cadastro Geral de um conjunto de pessoas que pedem o ingresso na escola - CGI"), ["CGI"])

    def test_nome_e_sigla_com_travessao(self):
        self.assertEqual(self.siglas("Coordenação-Geral de Ingresso - CGI"), [])
        self.assertEqual(self.siglas("Coordenação-Geral de Autorização para Transferência, Cisão e Retirada – CGTR"), [])
        self.assertEqual(self.siglas("Obter diploma ou 2ª via de diploma - IFTO"), ["IFTO"])
        self.assertEqual(self.siglas("Ingresso - CGI"), ["CGI"])

    def test_nome_proprio_em_qualquer_ponto_antes(self):
        self.assertEqual(self.siglas("Pagar a Guia de Recolhimento da União.\n\nEmita a GRU."), [])
        self.assertEqual(self.siglas("Pagar a guia de recolhimento da união.\n\nEmita a GRU."), ["GRU"])
        self.assertEqual(self.siglas("Pagar a Guia de Pagamento e Recolhimento da União. Emita a GRU."), ["GRU"])
        self.assertEqual(self.siglas("Emita a GRU. Pague a Guia de Recolhimento da União."), ["GRU"])
        self.assertEqual(self.siglas("A Guia de Recolhimento da União vence hoje. Emita a GRU."), [])
        # O nome tem de estar inteiro: na amostra, o fluxo "Informar Mudança de
        # Endereço de Curso" fazia passar o MEC da página.
        self.assertEqual(self.siglas("Use “Informar Mudança de Endereço de Curso” no sistema do MEC."), ["MEC"])
        self.assertEqual(self.siglas("Use Mudança, Endereço e Curso no sistema do MEC."), ["MEC"])
        self.assertEqual(self.siglas("Guia\nRecolhimento\nUnião.\n\nEmita a GRU."), ["GRU"])

    def test_hifen_dentro_da_palavra_nao_liga(self):
        # Na amostra, "Sistema e-MEC" e "Brasília-DF".
        self.assertEqual(self.siglas("Informar Mudança de Endereço de Curso do Sistema e-MEC."), ["MEC"])

    def test_nome_ligado_pula_no_maximo_duas_palavras(self):
        self.assertEqual(self.siglas("Departamento de Operações de Comércio Exterior – DECEX"), [])
        self.assertEqual(self.siglas("Lei Geral de Proteção de Dados Pessoais - LGPD"), [])
        # Na amostra, "Complementar do Exército - Rua ... Pituba, Salvador/BA - CEP".
        self.assertEqual(self.siglas("Colégio Estadual na Rua Nova do Porto - CEP"), ["CEP"])

    # Os casos a seguir vêm dos erros da 2ª amostra (corpus/amostra-2.md,
    # 09/10/2026).
    def test_endereco_nao_tem_sigla(self):
        self.assertEqual(self.siglas("Avalie o serviço no Portal GOV.BR"), [])
        self.assertEqual(self.siglas("Veja https://exemplo.gov.br/resolu%C3%A7%C3%A3o-n%C2%BA-1"), [])
        self.assertEqual(self.siglas("Escreva para SAC@exemplo.gov.br."), [])
        self.assertEqual(self.siglas("Procure o INSS. Depois, o MEC."), ["INSS", "MEC"])

    def test_palavra_comum_em_caixa_alta(self):
        self.assertEqual(self.siglas("SISTEMA SIMEC. Entre no sistema."), ["SIMEC"])
        self.assertEqual(self.siglas("SISTEMA SIMEC."), ["SISTEMA", "SIMEC"])
        self.assertEqual(self.siglas("Acesse SISTEMA. Veja www.sistema.gov.br."), ["SISTEMA"])
        self.assertEqual(self.siglas("Acesse SISTEMA. Veja https://exemplo.gov.br?busca=sistema"), ["SISTEMA"])
        # Na 3ª amostra, "e-SISBI" e o link "(inspecao/e-sisbi)".
        self.assertEqual(self.siglas("Use o SISBI. Acesse (inspecao/e-sisbi)."), ["SISBI"])
        self.assertEqual(self.siglas("Use o SISBI. Acesse sisbi-web ou sisbi/consulta."), ["SISBI"])
        # Com quatro letras, sigla e palavra se confundem: MAPA continua.
        self.assertEqual(self.siglas("Fale com o MAPA. Veja o mapa."), ["MAPA"])

    def test_nome_com_hifen(self):
        texto = "Fale com a Procuradoria-Geral da Fazenda Nacional.\n\nProposta da PGFN."
        self.assertEqual(self.siglas(texto), [])
        self.assertEqual(self.siglas("Fale com a Procuradoria-geral da Fazenda Nacional.\n\nA PGFN."), [])
        self.assertEqual(self.siglas("Fale com a Procuradoria Geral.\n\nProposta da PGFN."), ["PGFN"])
        self.assertEqual(self.siglas("Use o e-Fazenda Nacional.\n\nProposta da PGFN."), ["PGFN"])

    def test_nome_ligado_a_sigla_em_outra_caixa(self):
        texto = "Serviço da Secretaria Nacional de Trânsito — Senatran. Use o SENATRAN."
        self.assertEqual(self.siglas(texto), [])
        self.assertEqual(self.siglas("SECRETARIA NACIONAL DE TRÂNSITO — SENATRAN\n\nUse o SENATRAN."), [])
        self.assertEqual(self.siglas("Serviço da Senatran. Use o SENATRAN."), ["SENATRAN"])
        self.assertEqual(self.siglas("Use o SENATRAN. Secretaria Nacional de Trânsito — Senatran."), ["SENATRAN"])

    def test_romano_caixa_alta_acento_e_plural(self):
        self.assertEqual(self.siglas("Leia o inciso XI, o capítulo CC e o século XX."), [])
        self.assertEqual(self.siglas("Dom Pedro II assinou."), [])
        self.assertEqual(self.siglas("O CC regula o tema."), ["CC"])
        self.assertEqual(self.siglas("ATENÇÃO: O PRAZO TERMINA HOJE"), [])
        self.assertEqual(self.siglas("Ele disse “NÃO” ao pedido."), [])
        self.assertEqual(self.siglas("As ONGs e a ONG."), ["ONGs"])

    def test_ignorar(self):
        self.assertEqual(siglas_sem_nome("Informe o CPF.", ignorar=["cpf"]), [])

    def test_texto_bom_do_guia(self):
        self.assertEqual(self.siglas(guias.SIGLA_CAPES.depois), [])
        self.assertEqual(self.siglas(guias.ANVISA_SEI_DEPOIS), [])
        self.assertEqual(self.siglas(guias.TREAL_PARAGRAFOS), [])

    def test_par_antes_conta_mais(self):
        par = guias.SIGLA_CAPES
        self.assertEqual((len(self.siglas(par.antes)), len(self.siglas(par.depois))), (1, 0))

    @unittest.expectedFailure
    def test_sigla_escrita_como_nome_proprio(self):
        # Limite conhecido: sigla com só a inicial maiúscula ("Lacen",
        # "Anvisa") não se distingue de nome próprio sem um léxico com fonte.
        par = guias.SIGLA_ANVISA_LACEN
        self.assertGreater(len(self.siglas(par.antes)), len(self.siglas(par.depois)))


def trechos(detector, texto):
    return [o.trecho for o in detector(texto)]


class TestIncisoXII(unittest.TestCase):
    def test_plantado(self):
        achadas = voz_passiva("O pedido foi analisado pela equipe.")
        self.assertEqual([(o.inciso, o.trecho, o.inicio) for o in achadas], [("XII", "foi analisado", 9)])
        self.assertIn("com agente", achadas[0].mensagem)
        self.assertIn("sem agente", voz_passiva("Os documentos serão conferidos.")[0].mensagem)

    def test_formas_e_particípios(self):
        self.assertEqual(trechos(voz_passiva, "A obra foi concluída."), ["foi concluída"])
        self.assertEqual(trechos(voz_passiva, "Se o pedido for aprovado, avise."), ["for aprovado"])
        self.assertEqual(trechos(voz_passiva, "Foi rapidamente aprovado."), ["Foi rapidamente aprovado"])
        self.assertEqual(trechos(voz_passiva, "O ofício tinha sido entregue."), ["sido entregue"])

    def test_nao_e_passiva(self):
        for texto in (
            "O documento é válido.",            # adjetivo com acento antes de -ido
            "A reunião é no sábado.",           # substantivo
            "Ele mora em São Conrado.",         # nome próprio
            "O pedido está aprovado.",          # estar, não ser
            "A empresa entregou o documento.",  # voz ativa
        ):
            with self.subTest(texto):
                self.assertEqual(voz_passiva(texto), [])

    def test_por_meio_nao_e_agente(self):
        self.assertIn("sem agente", voz_passiva("A entrega é feita por meio do portal.")[0].mensagem)

    def test_agente_so_na_mesma_oracao(self):
        self.assertIn("sem agente", voz_passiva("O pedido foi negado, por isso recorra.")[0].mensagem)

    def test_texto_bom_e_par_do_guia(self):
        for par in guias.PASSIVA:
            with self.subTest(par.antes):
                self.assertEqual(voz_passiva(par.depois), [])
                self.assertEqual(len(voz_passiva(par.antes)), 1)

    def test_texto_corrido_dos_guias_tem_passiva(self):
        # Medido em 09/10/2026: o texto que os guias dão como bom em outras
        # técnicas usa voz passiva. A lei diz "preferencialmente na voz
        # ativa"; o detector aponta, quem lê decide.
        self.assertEqual(trechos(voz_passiva, guias.TREAL_PARAGRAFOS), ["ser utilizadas"])
        self.assertEqual(trechos(voz_passiva, guias.ANVISA_SEI_DEPOIS), ["ser punido"])
        self.assertEqual(trechos(voz_passiva, guias.FRASE_ANVISA.depois), ["é feita", "ser notificados"])
        self.assertEqual(trechos(voz_passiva, guias.SIGLA_CAPES.depois), ["será feito"])
        self.assertEqual(trechos(voz_passiva, guias.FRASE_TJGO.depois), [])
        self.assertEqual(trechos(voz_passiva, guias.FRASE_CAPES.depois), [])

    @unittest.expectedFailure
    def test_par_da_capes_sem_verbo_na_passiva(self):
        # Limite conhecido: "é responsabilidade da CAPES" não é voz passiva
        # na gramática, embora o guia o use como exemplo dela.
        par = guias.PASSIVA_CAPES
        self.assertGreater(len(voz_passiva(par.antes)), len(voz_passiva(par.depois)))


class TestIncisoXIII(unittest.TestCase):
    def test_plantado(self):
        texto = "O prazo, que termina amanhã, vale para todos."
        achadas = frases_intercaladas(texto)
        self.assertEqual([(o.inciso, o.trecho) for o in achadas], [("XIII", "que termina amanhã")])
        self.assertEqual(texto[achadas[0].inicio:achadas[0].fim], "que termina amanhã")

    def test_relativos(self):
        self.assertEqual(len(frases_intercaladas("O órgão, o qual responde ao ministério, decide.")), 1)
        self.assertEqual(len(frases_intercaladas("O cidadão, cujo pedido foi negado, pode recorrer.")), 1)
        self.assertEqual(len(frases_intercaladas("A sala, onde fica o arquivo, está fechada.")), 1)

    def test_nao_e_intercalada(self):
        for texto in (
            "Traga o RG, o CPF e o comprovante.",       # lista
            "O importante, nestes casos, é evitar.",   # sem relativo
            "Leve o documento, que é obrigatório.",    # fecha a frase, não intercala
            "Pague logo, que o prazo é de 1,5 dia.",   # vírgula de número não fecha o trecho
        ):
            with self.subTest(texto):
                self.assertEqual(frases_intercaladas(texto), [])

    def test_texto_bom_e_par_do_guia(self):
        par = guias.INTERCALADA_CAPES
        self.assertEqual((len(frases_intercaladas(par.antes)), len(frases_intercaladas(par.depois))), (1, 0))
        for texto in (guias.TREAL_PARAGRAFOS, guias.ANVISA_SEI_DEPOIS, guias.FRASE_CAPES.depois,
                      guias.FRASE_ANVISA.depois, guias.FRASE_TJGO.depois):
            with self.subTest(texto[:30]):
                self.assertEqual(frases_intercaladas(texto), [])


class TestIncisoXIV(unittest.TestCase):
    def test_plantado(self):
        achadas = substantivos_no_lugar_de_verbos("Faça o pagamento da taxa.")
        self.assertEqual([(o.inciso, o.trecho) for o in achadas], [("XIV", "Faça o pagamento")])
        self.assertIn("pagar", achadas[0].mensagem)

    def test_verbo_de_apoio_com_substantivo_fora_do_lexico(self):
        achadas = substantivos_no_lugar_de_verbos("O órgão fará a avaliação do caso.")
        self.assertEqual([o.trecho for o in achadas], ["fará a avaliação"])
        self.assertNotIn("verbo:", achadas[0].mensagem)
        self.assertEqual(len(substantivos_no_lugar_de_verbos("O fiscal fez o levantamento.")), 1)

    def test_lexico_com_complemento_e_plural(self):
        self.assertEqual(trechos(substantivos_no_lugar_de_verbos, "Solicitações de acesso."), ["Solicitações"])
        self.assertEqual(trechos(substantivos_no_lugar_de_verbos, "A análise terminou."), [])
        self.assertEqual(trechos(substantivos_no_lugar_de_verbos, "Os pagamentos do mês."), ["pagamentos"])

    def test_lexico_tem_fonte_em_cada_entrada(self):
        caminho = Path(detectores.__file__).parent / "lexicos" / "nominalizacoes.txt"
        for linha in caminho.read_text(encoding="utf-8").splitlines():
            if linha.strip() and not linha.startswith("#"):
                with self.subTest(linha):
                    palavra, verbo, fonte = (c.strip() for c in linha.split("|"))
                    self.assertTrue(palavra and verbo)
                    self.assertRegex(fonte, r"p\. \d+")

    def test_texto_bom_e_pares_do_guia(self):
        for par in guias.NOMINALIZACAO:
            with self.subTest(par.antes):
                self.assertGreater(len(substantivos_no_lugar_de_verbos(par.antes)), 0)
                self.assertEqual(substantivos_no_lugar_de_verbos(par.depois), [])
        for texto in (guias.TREAL_PARAGRAFOS, guias.ANVISA_SEI_DEPOIS, guias.FRASE_CAPES.depois,
                      guias.FRASE_ANVISA.depois, guias.FRASE_TJGO.depois):
            with self.subTest(texto[:30]):
                self.assertEqual(substantivos_no_lugar_de_verbos(texto), [])

    def test_apoio_com_substantivo_que_nao_e_de_verbo(self):
        self.assertEqual(substantivos_no_lugar_de_verbos("Faça a prova e o curso."), [])

    def test_ordem_do_texto(self):
        achadas = substantivos_no_lugar_de_verbos("Solicitação de bolsa: faça o pagamento.")
        self.assertEqual([o.trecho for o in achadas], ["Solicitação", "faça o pagamento"])

    def test_apoio_nao_conta_duas_vezes(self):
        achadas = substantivos_no_lugar_de_verbos("Farão a análise do pedido de ampliação da vacina.")
        self.assertEqual([o.trecho for o in achadas], ["Farão a análise", "ampliação"])


if __name__ == "__main__":
    unittest.main()
