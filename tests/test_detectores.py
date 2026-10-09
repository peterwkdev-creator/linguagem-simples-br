"""Duas provas por detector: pega o defeito plantado e não dispara no texto
que o guia oficial dá como bom. E, em cada par do guia, o "antes" conta mais
que o "depois"."""

import unittest

from linguagem_simples import limiares
from linguagem_simples.detectores import frases_longas, paragrafos_longos, siglas_sem_nome

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

    def test_iniciais_em_ordem_com_palavras_no_meio(self):
        texto = (
            "A Secretaria Especial da Receita Federal do Brasil (RFB) e o "
            "Sistema Único de Saúde (SUS)."
        )
        self.assertEqual(self.siglas(texto), [])

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


if __name__ == "__main__":
    unittest.main()
