"""Duas provas por detector: pega o defeito plantado e não dispara no texto
que o guia oficial dá como bom. E, em cada par do guia, o "antes" conta mais
que o "depois"."""

import unittest
from pathlib import Path

from linguagem_simples import detectores, limiares
from linguagem_simples.detectores import (
    acessibilidade, frases_intercaladas, frases_longas, paragrafos_longos, redundancias,
    siglas_sem_nome, substantivos_no_lugar_de_verbos, voz_passiva,
)
from linguagem_simples.pagina import ler_html

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

    # Os dois a seguir vêm dos erros da 3ª amostra (corpus/amostra-3.md, 09/10/2026).
    def test_cor_em_caixa_alta(self):
        texto = "Prioridade: VERMELHO - Emergência, AZUL - Não Urgente."
        self.assertEqual(self.siglas(texto), [])
        self.assertEqual(self.siglas("Bandeira VERMELHA no posto."), [])
        self.assertEqual(self.siglas("Fila VERDE. Procure o SUS."), ["SUS"])

    def test_data_de_epigrafe(self):
        texto = "Leia a RDC Nº 513, DE 27 DE MAIO DE 2021, e a RDC Nº 1, DE 1º DE MARÇO DE 2020. Procure o SUS."
        self.assertEqual(self.siglas(texto), ["RDC", "SUS"])
        self.assertEqual(self.siglas("A ação vai DE 27 DE MAIO a junho."), [])
        self.assertEqual(self.siglas("O prazo de 27 DE MAIO. Leia o DE 4."), ["DE", "MAIO"])
        self.assertEqual(self.siglas("Leia o DE 4 DE SUS."), ["DE", "SUS"])

    # Os três a seguir também vêm dos erros da 3ª amostra: o nome vinha antes.
    def test_nome_dentro_de_nome_maior(self):
        texto = "Serviço da Secretaria Especial da Receita Federal do Brasil.\n\nLeia a Instrução RFB nº 1."
        self.assertEqual(self.siglas(texto), [])
        self.assertEqual(self.siglas("Serviço da Receita Federal.\n\nLeia a Instrução RFB nº 1."), ["RFB"])
        # O pedaço começa depois de um conectivo e vai até o fim do nome.
        self.assertEqual(self.siglas("Serviço da Secretaria Receita Federal Brasil.\n\nLeia a RFB."), ["RFB"])
        self.assertEqual(self.siglas("Serviço da Receita Federal do Brasil Digital.\n\nLeia a RFB."), ["RFB"])
        # Com duas letras, só o nome inteiro: na 2ª amostra, a PF (Polícia
        # Federal) depois do "Cadastro de Pessoa Física".
        self.assertEqual(self.siglas("Leve o Cadastro de Pessoa Física.\n\nCursos na PF."), ["PF"])
        self.assertEqual(self.siglas("Leve a Pessoa Física.\n\nCursos na PF."), [])

    def test_nome_colado_a_sigla(self):
        texto = "No âmbito da Divisão de Cooperação e Intercâmbio DICIN/INPA."
        self.assertEqual(self.siglas(texto), ["INPA"])
        self.assertEqual(self.siglas("Fale com a Divisão de Cooperação e Intercâmbio. A DICIN atende."), ["DICIN"])
        self.assertEqual(self.siglas("Fale com a Divisão de Cooperação e Intercâmbio, DICIN."), ["DICIN"])
        self.assertEqual(self.siglas("Divisão de Cooperação e Intercâmbio\nDICIN"), ["DICIN"])

    def test_nome_com_contracao_de_em(self):
        for contracao in ("no", "na", "nos", "nas"):
            texto = f"Saúde e Segurança {contracao} Trabalho\n\nBaixe o SST Fácil."
            self.assertEqual(self.siglas(texto), [], contracao)
        self.assertEqual(self.siglas("Curso de Saúde no Sistema Único de Saúde.\n\nUse o SUS."), [])
        self.assertEqual(self.siglas("No Instituto Nacional do Seguro Social, procure o INSS."), [])
        self.assertEqual(self.siglas("Saúde e Segurança pelo Trabalho\n\nBaixe o SST Fácil."), ["SST"])
        self.assertEqual(self.siglas("Saúde e Segurança no trabalho\n\nBaixe o SST Fácil."), ["SST"])

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

    def test_nome_de_documento_antes(self):
        for texto in ("Guia de Recolhimento da União", "Documento de identificação da criança",
                      "Anexe o comprovante de pagamento da taxa.", "Dados de identificação do solicitante",
                      "Cartões de Pagamento da Defesa Civil", "Baixe os formulários de solicitação do serviço."):
            with self.subTest(texto):
                self.assertEqual(substantivos_no_lugar_de_verbos(texto), [])
        self.assertEqual(trechos(substantivos_no_lugar_de_verbos, "durante o tempo de análise da documentação"),
                         ["análise"])
        self.assertEqual(trechos(substantivos_no_lugar_de_verbos, "Junte a guia do pagamento da taxa."), ["pagamento"])
        self.assertEqual(trechos(substantivos_no_lugar_de_verbos, "Envie o comprovante de residência e a análise do laudo."),
                         ["análise"])

    def test_lexico_de_documentos_tem_fonte(self):
        caminho = Path(detectores.__file__).parent / "lexicos" / "documentos.txt"
        for linha in caminho.read_text(encoding="utf-8").splitlines():
            if linha.strip() and not linha.startswith("#"):
                with self.subTest(linha):
                    palavra, acepcao, fonte = (c.strip() for c in linha.split("|"))
                    self.assertTrue(palavra and acepcao)
                    self.assertRegex(fonte, r'^Dicionário Priberam, verbete "\w+"')


class TestIncisoXV(unittest.TestCase):
    def test_plantado(self):
        achadas = redundancias("Compareça pessoalmente ao local.")
        self.assertEqual([(o.inciso, o.trecho) for o in achadas], [("XV", "Compareça pessoalmente")])
        self.assertEqual((achadas[0].inicio, achadas[0].fim), (0, len("Compareça pessoalmente")))
        self.assertIn("“comparecer”", achadas[0].mensagem)

    def test_verbo_conjugado_e_plural(self):
        self.assertEqual(trechos(redundancias, "Ele entrou para dentro e depois saiu para fora."),
                         ["entrou para dentro", "saiu para fora"])
        self.assertEqual(trechos(redundancias, "Desça para baixo; ele sobe para cima."),
                         ["Desça para baixo", "sobe para cima"])
        self.assertEqual(trechos(redundancias, "As conclusões finais, na data acima citada."),
                         ["conclusões finais", "acima citada"])

    def test_palavra_inteira(self):
        self.assertEqual(trechos(redundancias, "A FIM DE votar, um pequeno número de eleitores."),
                         ["A FIM DE", "um pequeno número"])
        for texto in ("Ele está de acordo comigo.", "Um termo afim de outro.", "Vou entrar.",
                      "com vistas", "Subir para a cima.", "Leve a mesa para fora."):
            with self.subTest(texto):
                self.assertEqual(redundancias(texto), [])

    def test_quebra_de_linha_sim_paragrafo_nao(self):
        self.assertEqual(trechos(redundancias, "Pague de acordo \n com a tabela."), ["de acordo \n com"])
        self.assertEqual(trechos(redundancias, "Pague de  acordo com a tabela."), ["de  acordo com"])
        self.assertEqual(redundancias("Pague de acordo\n\ncom a tabela."), [])

    def test_crase_e_artigo(self):
        self.assertEqual(trechos(redundancias, "Com vistas à posse e com vistas aos prazos."),
                         ["Com vistas à", "com vistas aos"])

    def test_texto_bom_e_par_do_guia(self):
        par = guias.REDUNDANCIA_CAPES
        self.assertEqual((len(redundancias(par.antes)), len(redundancias(par.depois))), (1, 0))
        bons = [guias.TREAL_PARAGRAFOS, guias.ANVISA_SEI_DEPOIS, guias.FRASE_CAPES.depois,
                guias.FRASE_ANVISA.depois, guias.FRASE_TJGO.depois, guias.INTERCALADA_CAPES.depois]
        bons += [p.depois for p in guias.PASSIVA + guias.NOMINALIZACAO]
        for texto in bons:
            with self.subTest(texto[:30]):
                self.assertEqual(redundancias(texto), [])

    def test_lexico_de_redundancias_tem_fonte(self):
        caminho = Path(detectores.__file__).parent / "lexicos" / "redundancias.txt"
        linhas = [l for l in caminho.read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")]
        self.assertEqual(len(linhas), 29)
        for linha in linhas:
            with self.subTest(linha):
                expressao, forma, fonte = (c.strip() for c in linha.split("|"))
                self.assertTrue(expressao and forma)
                self.assertRegex(fonte, r"^(?:TRE-AL p\. 1[67] \(1[45]\)|CJF p\. 9|CAPES p\. 11 \(10\))")


def xvii(html):
    """Mensagem e trecho de cada achado do XVII no HTML."""
    return [(o.mensagem.split()[0], o.trecho) for o in acessibilidade(ler_html(html))]


class TestIncisoXVII(unittest.TestCase):
    def test_plantado(self):
        html = ('<p>Para o formulário, <a href="f.pdf">clique aqui</a>.</p><img src="mapa.png">'
                "<table><tr><td>Taxa</td><td>R$ 10</td></tr></table>")
        pagina = ler_html(html)
        achadas = acessibilidade(pagina)
        self.assertEqual([(o.mensagem.split()[0], o.trecho) for o in achadas],
                         [("link", "clique aqui"), ("imagem", '<img src="mapa.png">'), ("tabela", "Taxa\n\nR$ 10")])
        self.assertEqual([o.inciso for o in achadas], ["XVII"] * 3)
        link, imagem, tabela = achadas
        self.assertIn("eMAG 3.5", link.mensagem)
        self.assertIn("eMAG 3.6", imagem.mensagem)
        self.assertIn("eMAG 3.10", tabela.mensagem)
        self.assertEqual(link.no_html, (html.index("<a "), html.index("</a>") + 4))
        self.assertEqual(pagina.texto[link.inicio:link.fim], "clique aqui")
        self.assertEqual(imagem.no_html, (html.index("<img"), html.index("<table")))
        self.assertEqual(tabela.no_html, (html.index("<table"), len(html)))

    def test_texto_do_link_inteiro_maiuscula_e_pontuacao(self):
        for texto in ("Saiba mais", "SAIBA MAIS", " saiba  mais. ", "Clique aqui!", "» Leia mais",
                      "<b>Aqui</b>", "neste link", "Acesse o site", "mais", "mais informações",
                      "Clique aqui para saber mais.", "(acesse)", "Consultar", "Inscreva-se", "Android", "iOS"):
            with self.subTest(texto):
                self.assertEqual([t for t, _ in xvii(f'<a href="x">{texto}</a>')], ["link"])
        # verbo com o objeto e loja com o nome dizem o destino
        for texto in ("Saiba mais sobre o cadastro", "Leia mais notícias", "Aquiraz", "Mais informações sobre o FGTS",
                      "Clique aqui para agendar", "Consultar a situação do CPF", "Google Play", "Apple Store",
                      "Acessibilidade", "Webinário"):
            with self.subTest(texto):
                self.assertEqual(xvii(f'<a href="x">{texto}</a>'), [])

    def test_nome_do_link(self):
        # aria-label vale como texto do link; title não (eMAG 3.5)
        self.assertEqual(xvii('<a href="x" aria-label="Saiba mais sobre a conta gov.br">Saiba mais</a>'), [])
        self.assertEqual(xvii('<a href="x" aria-label="Saiba mais">Conta gov.br</a>'),
                         [("link", "Conta gov.br")])
        self.assertEqual(len(xvii('<a href="x" title="Saiba mais sobre a conta gov.br">Saiba mais</a>')), 1)
        self.assertEqual(xvii('<a href="x" aria-labelledby="t">Saiba mais</a>'), [])
        # o alt da imagem dentro do link entra no texto dele
        self.assertEqual(xvii('<a href="x"><img src="i.png" alt="Aqui"></a>'), [("link", "")])
        self.assertEqual(xvii('<a href="x"><img src="i.png" alt="Formulário de inscrição"></a>'), [])
        # âncora sem href não é link
        self.assertEqual(xvii('<a name="topo">aqui</a>'), [])

    def test_imagem_e_tabela_dispensadas(self):
        bons = ('<img src="a.png" alt="">', '<img src="a.png" role="presentation">',
                '<img src="a.png" role="none">', '<img src="a.png" aria-hidden="true">',
                '<img src="a.png" aria-label="Mapa">', '<img src="a.png" aria-labelledby="legenda">',
                '<table role=" Presentation "><tr><td>a</td></tr></table>',
                '<table><tr><th scope="row">Taxa</th><td>R$ 10</td></tr></table>')
        for html in bons:
            with self.subTest(html):
                self.assertEqual(xvii(html), [])

    def test_trecho_sem_o_espaco_das_pontas(self):
        pagina = ler_html('<p>Veja<a href="x"> aqui </a>de novo.</p>')
        (o,) = acessibilidade(pagina)
        self.assertEqual((o.trecho, pagina.texto[o.inicio:o.fim]), ("aqui", "aqui"))

    def test_fechamento_sem_abertura(self):
        self.assertEqual(xvii("<p>Texto</table></a>.</p>"), [])

    def test_tabela_dentro_de_tabela(self):
        html = "<table><tr><th>A</th><td><table><tr><td>b</td></tr></table></td></tr></table>"
        self.assertEqual(xvii(html), [("tabela", "b")])
        html = "<table><tr><td>a</td><td><table><tr><th>B</th></tr></table></td></tr></table>"
        self.assertEqual(xvii(html), [("tabela", "a\n\nB")])

    def test_so_o_que_o_leitor_le(self):
        html = ('<nav><a href="x">Saiba mais</a></nav><div hidden><img src="a.png"></div>'
                '<main><a href="y">aqui</a></main><footer><a href="z">aqui</a></footer>')
        self.assertEqual(xvii(html), [("link", "aqui")])

    def test_markdown(self):
        texto = "Veja [clique aqui](https://a.gov.br), [o edital](e.pdf) e ![aqui](i.png)."
        self.assertEqual(trechos(acessibilidade, texto), ["[clique aqui](https://a.gov.br)"])
        self.assertEqual(trechos(acessibilidade, "[Saiba  mais](s.html)"), ["[Saiba  mais](s.html)"])
        self.assertEqual(acessibilidade("Clique aqui para ver."), [])

    def test_texto_bom_e_par_do_guia(self):
        par = guias.LINK_EMAG
        self.assertEqual((len(xvii(par.antes)), len(xvii(par.depois))), (1, 0))
        for html in guias.BONS_EMAG:
            with self.subTest(html[:30]):
                self.assertEqual(xvii(html), [])

    def test_lexico_de_links_tem_fonte(self):
        caminho = Path(detectores.__file__).parent / "lexicos" / "links-vagos.txt"
        linhas = [l for l in caminho.read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")]
        self.assertEqual(len(linhas), 46)
        origens, textos = [], []
        for linha in linhas:
            with self.subTest(linha):
                texto, origem, fonte = (c.strip() for c in linha.split("|"))
                self.assertEqual(texto, texto.casefold())
                self.assertIn(origem, ("lista", "regra", "verbo", "plataforma"))
                self.assertTrue(fonte.startswith("eMAG 3.1, Recomendação 3.5"))
                origens.append(origem)
                textos.append(texto)
        self.assertEqual([origens.count(o) for o in ("lista", "regra", "verbo", "plataforma")], [6, 16, 19, 5])
        self.assertEqual(len(set(textos)), len(textos))


if __name__ == "__main__":
    unittest.main()
