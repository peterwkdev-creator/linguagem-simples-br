"""Linha de comando: ``python -m linguagem_simples arquivo.txt`` (ou
``.html``).

Código de saída: 0 sem ocorrências, 1 com ocorrências, 2 erro de uso ou de
leitura. Com ``--reescrever``: 0 reescrita aceita (ou nada a reescrever),
1 recusada, 2 erro.
"""

import argparse
import json
import sys
from pathlib import Path

from . import __version__, reescrita
from .pagina import decodificar, ler_html, parece_html
from .relatorio import AVISO, como_dict, como_texto, conferir


def _positivo(valor):
    n = int(valor)
    if n < 1:
        raise argparse.ArgumentTypeError("use um número inteiro maior que zero")
    return n


def _ler(arquivo, html):
    """O que conferir: o próprio texto ou, no HTML, a ``Pagina``."""
    dados = sys.stdin.buffer.read() if arquivo == "-" else Path(arquivo).read_bytes()
    if html or Path(arquivo).suffix.lower() in (".html", ".htm") or parece_html(dados):
        return ler_html(decodificar(dados))
    return dados.decode("utf-8-sig")


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
    p.add_argument("--reescrever", action="store_true",
                   help="pede à IA (Claude, com a sua chave em %s) uma reescrita e só a "
                   "aceita se o verificador medir menos apontamentos; o sentido é você "
                   "quem confere" % reescrita.VARIAVEL_DA_CHAVE)
    p.add_argument("--modelo", default=reescrita.MODELO_PADRAO, metavar="NOME",
                   help="com --reescrever: modelo da API (padrão %(default)s)")
    p.add_argument("--saida", metavar="ARQUIVO",
                   help="com --reescrever: grava o texto aceito neste arquivo (nunca no arquivo lido)")
    p.add_argument("--versao", "--version", action="version",
                   version=f"linguagem_simples {__version__}", help="mostra a versão e sai")
    a = p.parse_args(argv)
    if (a.saida or a.modelo != reescrita.MODELO_PADRAO) and not a.reescrever:
        p.error("--modelo e --saida só valem com --reescrever")
    if a.saida and a.arquivo != "-" and Path(a.saida).resolve() == Path(a.arquivo).resolve():
        p.error("--saida não pode ser o arquivo lido: a reescrita nunca grava por cima do original")

    try:
        origem = _ler(a.arquivo, a.html)
    except OSError as erro:
        p.error(f"não consegui ler {a.arquivo}: {erro.strerror or erro}")
    except UnicodeDecodeError:
        p.error(f"{a.arquivo} não está em UTF-8 nem no charset que declara")
    except LookupError as erro:
        p.error(f"{a.arquivo}: codificação desconhecida ({erro})")
    if a.reescrever:
        return _reescrever(p, a, origem)
    try:
        resultados = conferir(origem, a.max_palavras, a.max_frases, a.ignorar_sigla, a.ligar, a.desligar)
    except ValueError as erro:
        p.error(str(erro))

    if a.json:
        print(json.dumps(como_dict(resultados, origem), ensure_ascii=False, indent=2))
    else:
        print(como_texto(resultados, origem))
    return 1 if any(r.ocorrencias for r in resultados) else 0


def _reescrever(p, a, origem):
    """Código de saída: 0 aceita ou nada a reescrever, 1 recusada, 2 erro
    (sem chave, sem rede, resposta de erro da API)."""
    try:
        r = reescrita.reescrever(
            origem, modelo=a.modelo, max_palavras=a.max_palavras, max_frases=a.max_frases,
            ignorar_siglas=a.ignorar_sigla, ligar=a.ligar, desligar=a.desligar)
    except ValueError as erro:
        p.error(str(erro))
    except reescrita.ErroDeReescrita as erro:
        print(f"{p.prog}: reescrita: {erro}", file=sys.stderr)
        return 2
    destino = None
    if r.aceita and a.saida:
        try:
            Path(a.saida).write_text(r.texto + "\n", encoding="utf-8")
        except OSError as erro:
            p.error(f"não consegui gravar {a.saida}: {erro.strerror or erro}")
        destino = a.saida
    if a.json:
        print(json.dumps(reescrita.como_dict(r), ensure_ascii=False, indent=2))
    else:
        print(reescrita.como_texto(r, destino))
    return 0 if r.aceita or not r.tentativas else 1


if __name__ == "__main__":
    # Acentos em UTF-8 também quando a saída vai para arquivo ou pipe (no
    # Windows, o padrão seria a página de código local).
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(main())
