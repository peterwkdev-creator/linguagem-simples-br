"""O que o PyPI publica: o README instala pelo nome do pyproject, não tem
link que só funciona no GitHub, e o comando que o pip cria aponta para uma
função que existe (como no simples-nacional-br)."""

import importlib
import re
import tomllib
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]


class TestPyPI(unittest.TestCase):

    def setUp(self):
        self.projeto = tomllib.loads((RAIZ / "pyproject.toml").read_text(encoding="utf-8"))["project"]
        self.readme = (RAIZ / "README.md").read_text(encoding="utf-8")

    def test_readme_instala_pelo_nome_do_pyproject(self):
        self.assertIn(f"pip install {self.projeto['name']}\n", self.readme)

    def test_sem_link_relativo(self):
        # o PyPI mostra este README e não acha arquivo do repositório nem
        # âncora de título: até a 1.8.0, o GIF e o LICENSE não abriam lá.
        # O que está em código (o exemplo "[clique aqui](url)") não é link.
        texto = re.sub(r"```.*?```", "", self.readme, flags=re.S)
        texto = re.sub(r"`[^`\n]*`", "", texto)
        self.assertEqual(re.findall(r"\]\((?!https?://)([^)]*)\)", texto), [])

    def test_comandos_apontam_para_funcoes(self):
        # um alvo errado em [project.scripts] só quebra depois do pip install
        comandos = self.projeto.get("scripts", {})
        self.assertTrue(comandos)
        for nome, alvo in comandos.items():
            with self.subTest(comando=nome):
                modulo, funcao = alvo.split(":")
                self.assertTrue(callable(getattr(importlib.import_module(modulo), funcao)))


if __name__ == "__main__":
    unittest.main()
