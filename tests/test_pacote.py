"""O pacote instalado leva tudo o que lê do disco, e a versão tem uma fonte só."""

import tomllib
import unittest
from pathlib import Path

import linguagem_simples

RAIZ = Path(__file__).resolve().parent.parent


class TestPacote(unittest.TestCase):
    def test_lexicos_vao_na_instalacao(self):
        # Sem o package-data, o pip instala só o .py e o detector quebra
        # com FileNotFoundError (medido em 10/10/2026, num venv limpo).
        projeto = tomllib.loads((RAIZ / "pyproject.toml").read_text(encoding="utf-8"))
        padroes = projeto["tool"]["setuptools"]["package-data"]["linguagem_simples"]
        pacote = RAIZ / "linguagem_simples"
        dados = [p for p in pacote.rglob("*") if p.is_file() and p.suffix not in (".py", ".pyc")]
        self.assertTrue(dados)
        for p in dados:
            with self.subTest(p.name):
                self.assertTrue(any(p.relative_to(pacote).match(g) for g in padroes))

    def test_changelog_abre_com_a_versao(self):
        changelog = (RAIZ / "CHANGELOG.md").read_text(encoding="utf-8")
        primeira = next(l for l in changelog.splitlines() if l.startswith("## "))
        self.assertTrue(primeira.startswith(f"## {linguagem_simples.__version__} "))


if __name__ == "__main__":
    unittest.main()
