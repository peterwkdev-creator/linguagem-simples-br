"""O README: os exemplos em Python rodam como estão, e a instalação aponta a versão atual."""

import contextlib
import io
import re
import unittest
from pathlib import Path

README = Path(__file__).resolve().parents[1] / "README.md"


class TestExemplosDoReadme(unittest.TestCase):

    def test_blocos_python_rodam(self):
        blocos = re.findall(r"```python\n(.*?)```", README.read_text(encoding="utf-8"), re.S)
        self.assertGreaterEqual(len(blocos), 1)
        for i, bloco in enumerate(blocos, 1):
            # saída esperada e erro mostrado ficam em comentário, nunca solto
            # o print dos exemplos não sai no meio dos testes
            with self.subTest(bloco=i), contextlib.redirect_stdout(io.StringIO()):
                exec(compile(bloco, f"README, bloco {i}", "exec"), {})

    def test_instalar_pela_tag_da_versao_atual(self):
        from linguagem_simples import __version__
        # a tag pode aparecer mais de uma vez (pip e uv); o ponto final da
        # frase não entra (Coordenação, 10/10)
        tags = re.findall(r"linguagem-simples-br@v(\d+(?:\.\d+)*)", README.read_text(encoding="utf-8"))
        self.assertTrue(tags, "o README não manda instalar pela tag")
        self.assertEqual(set(tags), {__version__})


if __name__ == "__main__":
    unittest.main()
