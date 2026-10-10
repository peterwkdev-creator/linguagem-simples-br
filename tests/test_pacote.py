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
        # glob do Path, como o setuptools: o match da direita deixava
        # "lexicos/*.txt" valer em "sub/lexicos/x.txt" (Coordenação, 10/10)
        cobertos = {p for g in padroes for p in pacote.glob(g)}
        fora = [p.relative_to(pacote).as_posix() for p in dados if p not in cobertos]
        self.assertEqual(fora, [], "fora do package-data: não vão na instalação")

    def test_subpacotes_no_packages(self):
        # packages = ["linguagem_simples"] não leva subpasta com .py: o
        # import quebra só depois do pip install
        projeto = tomllib.loads((RAIZ / "pyproject.toml").read_text(encoding="utf-8"))
        pacotes = projeto["tool"]["setuptools"]["packages"]
        pacote = RAIZ / "linguagem_simples"
        subs = sorted({".".join(("linguagem_simples",) + p.parent.relative_to(pacote).parts)
                       for p in pacote.rglob("*.py") if "__pycache__" not in p.parts})
        self.assertEqual([s for s in subs if s not in pacotes], [])

    def test_changelog_abre_com_a_versao(self):
        changelog = (RAIZ / "CHANGELOG.md").read_text(encoding="utf-8")
        primeira = next(l for l in changelog.splitlines() if l.startswith("## "))
        self.assertTrue(primeira.startswith(f"## {linguagem_simples.__version__} "))


if __name__ == "__main__":
    unittest.main()
