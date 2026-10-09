import unittest

from linguagem_simples.texto import ITEM, PARAGRAFO, TITULO, blocos, palavras


class TestFrases(unittest.TestCase):
    def frases(self, texto):
        return [f.em(texto) for b in blocos(texto) for f in b.frases]

    def test_abreviatura_e_numero_nao_cortam_a_frase(self):
        texto = "O Sr. Silva leu o art. 5º da Lei 15.263. Ele pagou R$ 1.234,56!"
        self.assertEqual(
            self.frases(texto),
            ["O Sr. Silva leu o art. 5º da Lei 15.263.", "Ele pagou R$ 1.234,56!"],
        )

    def test_ponto_antes_de_minuscula_nao_corta(self):
        self.assertEqual(len(self.frases("Veja o site gov.br e depois. ligue")), 1)

    def test_frase_sem_ponto_final_conta(self):
        self.assertEqual(self.frases("Primeira. Segunda sem ponto"), ["Primeira.", "Segunda sem ponto"])

    def test_numero_conta_como_uma_palavra(self):
        self.assertEqual(palavras("R$ 1.234,56 em 09/10/2026"), ["R", "1.234,56", "em", "09/10/2026"])


class TestBlocos(unittest.TestCase):
    def test_tipos_e_posicoes(self):
        texto = "# Como pedir\r\n\r\nLinha um\r\ncontinua.\r\n\r\nVeja:\n- item um\n- item dois"
        achados = [(b.tipo, b.em(texto)) for b in blocos(texto)]
        self.assertEqual(achados, [
            (TITULO, "Como pedir"),
            (PARAGRAFO, "Linha um\r\ncontinua."),
            (PARAGRAFO, "Veja:"),
            (ITEM, "item um"),
            (ITEM, "item dois"),
        ])

    def test_ponto_medio_marca_item(self):
        # Assim as páginas de serviço do gov.br listam as diretrizes de atendimento.
        texto = "Diretrizes:\n· Urbanidade;\n· Respeito; e\n· Ética"
        self.assertEqual([(b.tipo, b.em(texto)) for b in blocos(texto)], [
            (PARAGRAFO, "Diretrizes:"), (ITEM, "Urbanidade;"), (ITEM, "Respeito; e"), (ITEM, "Ética"),
        ])

    def test_texto_vazio(self):
        self.assertEqual(blocos(""), [])
        self.assertEqual(blocos("\n\n  \n"), [])


if __name__ == "__main__":
    unittest.main()
