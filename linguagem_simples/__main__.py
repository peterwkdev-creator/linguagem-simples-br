"""Linha de comando: ``python -m linguagem_simples arquivo.txt`` (ou
``.html``).

Código de saída: 0 sem ocorrências, 1 com ocorrências, 2 erro de uso ou de
leitura.
"""

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .pagina import decodificar, ler_html, parece_html
from .relatorio import AVISO, como_dict, como_texto, conferir


def _positivo(valor):
    n = int(valor)
    if n < 1:
        raise argparse.ArgumentTypeError("use um número inteiro maior que zero")
    return n


def _ler(arquivo, html):
    """O texto a conferir e onde contar a posição: o próprio texto ou, no
    HTML, a ``Pagina``."""
    dados = sys.stdin.buffer.read() if arquivo == "-" else Path(arquivo).read_bytes()
    if html or Path(arquivo).suffix.lower() in (".html", ".htm") or parece_html(dados):
        pagina = ler_html(decodificar(dados))
        return pagina.texto, pagina
    texto = dados.decode("utf-8-sig")
    return texto, texto


def main(argv=None):
    p = argparse.ArgumentParser(
        prog="python -m linguagem_simples",
        description="Confere um texto contra os 18 incisos do art. 5º da Lei "
        "15.263/2025 (Política Nacional de Linguagem Simples). " + AVISO,
    )
    p.add_argument("arquivo", help="texto, Markdown ou HTML; '-' lê da entrada padrão")
    p.add_argument("--json", action="store_true", help="relatório em JSON")
    p.add_argument("--html", action="store_true",
                   help="lê como HTML (sem a opção: .html, .htm ou arquivo que começa por <!doctype html> ou <html>)")
    p.add_argument("--max-palavras", type=_positivo, metavar="N",
                   help="inciso II: palavras por frase (padrão 20)")
    p.add_argument("--max-frases", type=_positivo, metavar="N",
                   help="inciso III: frases por parágrafo (padrão 8)")
    p.add_argument("--ignorar-sigla", action="append", default=[], metavar="SIGLA",
                   help="inciso VIII: sigla que não precisa do nome (repetível)")
    p.add_argument("--ligar", action="append", default=[], metavar="INCISO",
                   help="liga um inciso desligado por padrão, como o XI (repetível)")
    p.add_argument("--desligar", action="append", default=[], metavar="INCISO",
                   help="desliga um inciso (repetível)")
    p.add_argument("--versao", "--version", action="version",
                   version=f"linguagem_simples {__version__}", help="mostra a versão e sai")
    a = p.parse_args(argv)

    try:
        texto, origem = _ler(a.arquivo, a.html)
    except OSError as erro:
        p.error(f"não consegui ler {a.arquivo}: {erro.strerror or erro}")
    except UnicodeDecodeError:
        p.error(f"{a.arquivo} não está em UTF-8 nem no charset que declara")
    except LookupError as erro:
        p.error(f"{a.arquivo}: codificação desconhecida ({erro})")
    try:
        resultados = conferir(texto, a.max_palavras, a.max_frases, a.ignorar_sigla, a.ligar, a.desligar)
    except ValueError as erro:
        p.error(str(erro))

    if a.json:
        print(json.dumps(como_dict(resultados, origem), ensure_ascii=False, indent=2))
    else:
        print(como_texto(resultados, origem))
    return 1 if any(r.ocorrencias for r in resultados) else 0


if __name__ == "__main__":
    # Acentos em UTF-8 também quando a saída vai para arquivo ou pipe (no
    # Windows, o padrão seria a página de código local).
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(main())
