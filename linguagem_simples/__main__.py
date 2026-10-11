"""Linha de comando: ``python -m linguagem_simples arquivo.txt`` (ou
``.html``).

Código de saída: 0 sem ocorrências, 1 com ocorrências, 2 erro de uso ou de
leitura. Com ``--reescrever``: 0 reescrita aceita (ou nada a reescrever),
1 recusada, 2 erro.
"""

import argparse
import getpass
import json
import os
import re
import sys
import textwrap
from pathlib import Path

from . import __version__, reescrita
from .pagina import decodificar, ler_html, parece_html
from .relatorio import AVISO, como_dict, como_texto, conferir, resumo


ISSUES = "https://github.com/peterwkdev-creator/linguagem-simples-br/issues"
VITRINE = "https://peterwkdev-creator.github.io/linguagem-simples-br/"

# Documento que não é texto: o começo do arquivo diz o que ele é.
_FORMATOS = (
    (b"PK\x03\x04", "um documento do Word (.docx), do LibreOffice (.odt) ou outro arquivo compactado"),
    (b"%PDF", "um PDF"),
    (b"\xd0\xcf\x11\xe0", "um documento do Word antigo (.doc)"),
    (b"{\\rtf", "um documento RTF"),
)

# As mensagens do argparse vêm em inglês; as que este comando pode dar.
_TRADUCOES = (
    (r"unrecognized arguments: (.+)", r"não entendi: \1 (um arquivo por vez; as opções estão em -h)"),
    (r"ambiguous option: (\S+) could match (.+)", r"\1 é ambíguo: pode ser \2"),
    (r"argument (\S+): expected one argument", r"\1 precisa de um valor logo depois"),
    (r"argument (\S+): ignored explicit argument (.+)", r"\1 não leva valor (veio \2)"),
    (r"argument (\S+): (.+)", r"\1: \2"),
)


def _nome_do_comando():
    # pelo pip, o nome do comando; por python -m, argv[0] é o caminho do .py
    if Path(sys.argv[0]).stem == "linguagem-simples":
        return "linguagem-simples"
    return "python -m linguagem_simples"


class _Formato(argparse.RawDescriptionHelpFormatter):
    def add_usage(self, usage, actions, groups, prefix=None):
        super().add_usage(usage, actions, groups, "uso: " if prefix is None else prefix)

    def _split_lines(self, text, width):
        # Sem quebrar no hífen: "claude-sonnet-5-5" fica numa linha só.
        return textwrap.wrap(" ".join(text.split()), width, break_on_hyphens=False)


class _Comando(argparse.ArgumentParser):
    """O argparse em português: ``uso:``, ``erro:`` e as mensagens dele."""

    def error(self, message):
        for padrao, troca in _TRADUCOES:
            if re.fullmatch(padrao, message, re.S):
                message = re.sub(padrao, troca, message, flags=re.S)
                break
        self.print_usage(sys.stderr)
        self.exit(2, f"{self.prog}: erro: {message}\n")


class _NaoETexto(Exception):
    """Documento que o verificador não lê: Word, PDF, RTF."""


def _positivo(valor):
    try:
        n = int(valor)
    except ValueError:
        n = 0
    if n < 1:
        raise argparse.ArgumentTypeError(f"use um número inteiro maior que zero, como 25 (veio {valor!r})")
    return n


def _ler(arquivo, html):
    """O que conferir (o próprio texto ou, no HTML, a ``Pagina``) e, se o
    texto não estava em UTF-8, a codificação em que foi lido."""
    dados = sys.stdin.buffer.read() if arquivo == "-" else Path(arquivo).read_bytes()
    for assinatura, nome in _FORMATOS:
        if dados.startswith(assinatura):
            raise _NaoETexto(nome)
    if dados.startswith((b"\xff\xfe", b"\xfe\xff")):  # o "Unicode" do Bloco de Notas
        dados = dados.decode("utf-16").encode("utf-8")
    if html or Path(arquivo).suffix.lower() in (".html", ".htm") or parece_html(dados):
        return ler_html(decodificar(dados)), None
    try:
        return dados.decode("utf-8-sig"), None
    except UnicodeDecodeError:
        # o "ANSI" do Bloco de Notas antigo; byte que nem ele tem sobe o erro
        return dados.decode("cp1252"), "Windows-1252"


def _exemplos(prog):
    exemplos = (
        ("mostra o relatório na tela", "carta.txt"),
        ("grava o relatório num arquivo novo", "carta.txt --saida relatorio.txt"),
        ("relatório em JSON, para outro programa", "pagina.html --json"),
        ("pede uma reescrita à IA (precisa de chave da API)", "carta.txt --reescrever"),
    )
    linhas = ["exemplos:"]
    for o_que, como in exemplos:
        linhas += [f"  {o_que}:", f"    {prog} {como}"]
    return "\n".join(linhas + [
        "",
        "código de saída: 0 nada a revisar, 1 há trechos a revisar, 2 erro.",
        f"sem instalar nada: cole o texto na vitrine, {VITRINE}",
    ])


def main(argv=None):
    prog = _nome_do_comando()
    p = _Comando(
        prog=prog,
        usage="%(prog)s arquivo [opções]",
        description=textwrap.fill(
            "Confere um texto, inciso por inciso, contra o art. 5º da Lei 15.263/2025 (Política "
            "Nacional de Linguagem Simples). " + AVISO, 79),
        epilog=_exemplos(prog),
        formatter_class=_Formato,
        add_help=False,
    )
    p._positionals.title = "arquivo"
    p._optionals.title = "opções"
    p.add_argument("arquivo", nargs="?",
                   help="o texto a conferir: .txt, .md ou .html; '-' lê o texto colado ou vindo de outro comando")
    p.add_argument("-h", "--ajuda", "--help", action="help", help="mostra esta ajuda e sai")
    p.add_argument("--json", action="store_true", help="relatório em JSON, para outro programa ler")
    p.add_argument("--html", action="store_true",
                   help="lê como HTML (sem a opção: .html, .htm ou arquivo que começa por <!doctype html> ou <html>)")
    p.add_argument("--max-palavras", type=_positivo, metavar="N",
                   help="inciso II: máximo de palavras por frase (padrão 20)")
    p.add_argument("--max-frases", type=_positivo, metavar="N",
                   help="inciso III: máximo de frases por parágrafo (padrão 8)")
    p.add_argument("--ignorar-sigla", action="append", default=[], metavar="SIGLA",
                   help="inciso VIII: sigla que o leitor já conhece e dispensa o nome por extenso, "
                   "como CPF (repetível)")
    p.add_argument("--ligar", action="append", default=[], metavar="INCISO",
                   help="liga um inciso desligado por padrão: hoje só o XI, que ainda não tem detector e por isso não muda o resultado (repetível)")
    p.add_argument("--desligar", action="append", default=[], metavar="INCISO",
                   help="desliga um inciso, como --desligar XII (repetível)")
    p.add_argument("--saida", metavar="ARQUIVO",
                   help="grava o resultado neste arquivo novo, nunca por cima de um que já existe: o "
                   "relatório ou, com --reescrever, o texto aceito")
    p.add_argument("--reescrever", action="store_true",
                   help="pede à IA (Claude, pela API da Anthropic, com a sua chave) uma reescrita "
                   "e a confere antes de mostrar (apontamentos, números, siglas, links e nomes); "
                   "o sentido é você "
                   "quem confere. A chave vem da variável %s ou, sem ela, é perguntada "
                   "na hora, sem aparecer na tela; nunca é gravada. Cada pedido é cobrado "
                   "na conta da chave" % reescrita.VARIAVEL_DA_CHAVE)
    p.add_argument("--modelo", default=reescrita.MODELO_PADRAO, metavar="NOME",
                   help="com --reescrever: modelo da API (padrão %(default)s)")
    p.add_argument("--versao", "--version", action="version",
                   version=f"linguagem_simples {__version__}", help="mostra a versão e sai")
    a = p.parse_args(argv)
    if a.arquivo is None:
        p.error(f"falta o arquivo a conferir. Exemplo: {prog} carta.txt (ajuda: {prog} -h; "
                f"sem instalar nada: {VITRINE})")
    if a.modelo != reescrita.MODELO_PADRAO and not a.reescrever:
        p.error("--modelo só vale com --reescrever")
    if a.saida and a.arquivo != "-" and Path(a.saida).resolve() == Path(a.arquivo).resolve():
        p.error("--saida não pode ser o arquivo lido: o verificador nunca grava por cima do original")
    if a.saida == "-":
        p.error("--saida -: sem --saida, o resultado já vai para a tela")
    if a.saida and Path(a.saida).exists():
        p.error(f"--saida: {a.saida} já existe; escolha outro nome (o verificador nunca grava por cima de um arquivo)")
    if a.saida and not Path(a.saida).resolve().parent.is_dir():
        p.error(f"--saida: a pasta de {a.saida} não existe")
    if a.arquivo != "-" and Path(a.arquivo).is_dir():
        p.error(f"{a.arquivo} é uma pasta: indique um arquivo dentro dela")

    if a.arquivo == "-" and _e_terminal():
        print("Cole o texto e, no fim, aperte Ctrl+Z e Enter (Windows) ou Ctrl+D (Linux e Mac).",
              file=sys.stderr)
    try:
        origem, lido_como = _ler(a.arquivo, a.html)
    except _NaoETexto as erro:
        p.error(f"{a.arquivo} parece ser {erro}, e o verificador lê só texto (.txt, .md) e HTML. "
                "Abra o documento, copie o texto, cole no Bloco de Notas e salve como .txt; ou cole "
                f"o texto na vitrine, sem instalar nada: {VITRINE}")
    except FileNotFoundError:
        p.error(f"não achei {a.arquivo}: confira o nome e a pasta (no PowerShell, 'dir' lista os arquivos "
                "da pasta em que você está; nome com espaço vai entre aspas: \"meu texto.txt\")")
    except OSError as erro:
        p.error(f"não consegui ler {a.arquivo}: {erro.strerror or erro}")
    except UnicodeDecodeError:
        p.error(f"{a.arquivo} não está em UTF-8 (nem no charset que declara, se for HTML): abra no "
                "Bloco de Notas e salve de novo com Arquivo > Salvar como > Codificação: UTF-8")
    except LookupError as erro:
        p.error(f"{a.arquivo}: codificação desconhecida ({erro})")
    if lido_como:
        print(f"{prog}: aviso: {a.arquivo} não está em UTF-8; foi lido como {lido_como}, o padrão antigo "
              "do Bloco de Notas. Se algum acento sair trocado, salve o arquivo de novo com "
              "Arquivo > Salvar como > Codificação: UTF-8.", file=sys.stderr)
    if a.reescrever:
        return _reescrever(p, a, origem)
    try:
        resultados = conferir(origem, a.max_palavras, a.max_frases, a.ignorar_sigla, a.ligar, a.desligar)
    except ValueError as erro:
        p.error(str(erro))

    if a.json:
        relatorio = json.dumps(como_dict(resultados, origem), ensure_ascii=False, indent=2)
    else:
        relatorio = como_texto(resultados, origem)
    if a.saida:
        try:
            with open(a.saida, "x", encoding="utf-8") as f:
                f.write(relatorio + "\n")
        except OSError as erro:
            p.error(f"não consegui gravar {a.saida}: {erro.strerror or erro}")
        print(f"Relatório gravado em {a.saida}. {resumo(resultados)}")
    else:
        print(relatorio)
    return 1 if any(r.ocorrencias for r in resultados) else 0


def _reescrever(p, a, origem):
    """Código de saída: 0 aceita ou nada a reescrever, 1 recusada, 2 erro
    (sem chave, sem rede, resposta de erro da API)."""
    try:
        r = reescrita.reescrever(
            origem, chave=lambda: _perguntar_chave(da_entrada_padrao=a.arquivo == "-"), modelo=a.modelo,
            max_palavras=a.max_palavras, max_frases=a.max_frases,
            ignorar_siglas=a.ignorar_sigla, ligar=a.ligar, desligar=a.desligar)
    except ValueError as erro:
        p.error(str(erro))
    except reescrita.ErroDeReescrita as erro:
        print(f"{p.prog}: reescrita: {erro}", file=sys.stderr)
        if any(erro.tokens):
            print(f"Uso da API até o erro: {erro.tokens[0]} tokens de entrada e {erro.tokens[1]} de saída, "
                  "cobrados pela Anthropic na conta da chave.", file=sys.stderr)
        return 2
    destino, codigo = None, 0 if r.aceita or not r.tentativas else 1
    if r.aceita and a.saida:
        try:
            with open(a.saida, "x", encoding="utf-8") as f:
                f.write(r.texto + "\n")
            destino = a.saida
        except OSError as erro:
            # A reescrita já foi paga: o texto vai para a tela em vez de se perder.
            print(f"{p.prog}: não consegui gravar {a.saida} ({erro.strerror or erro}); o texto vai abaixo.",
                  file=sys.stderr)
            codigo = 2
    if a.json:
        print(json.dumps(reescrita.como_dict(r), ensure_ascii=False, indent=2))
    else:
        print(reescrita.como_texto(r, destino))
    return codigo


def _e_terminal():
    """A entrada é um terminal em que se pode digitar. No Windows, o
    ``isatty`` também diz sim para o NUL (``< NUL``, ``< /dev/null``), e o
    ``getpass``, que lê do console, esperaria para sempre: lá se confere
    o console."""
    try:
        if not sys.stdin.isatty():
            return False
        if os.name != "nt":
            return True
        import ctypes
        import msvcrt
        modo = ctypes.c_ulong()
        return bool(ctypes.windll.kernel32.GetConsoleMode(msvcrt.get_osfhandle(sys.stdin.fileno()), ctypes.byref(modo)))
    except (AttributeError, OSError, TypeError, ValueError):
        return False


def _perguntar_chave(da_entrada_padrao=False):
    """Sem a variável de ambiente, pergunta a chave no terminal, sem mostrar
    o que se digita; ela fica só na memória, nesta execução."""
    chave = reescrita.chave_do_ambiente()
    if chave or not _e_terminal():
        return chave
    if da_entrada_padrao:
        raise reescrita.ErroDeReescrita(
            f"com o texto pela entrada padrão ('-'), a chave não tem como ser perguntada: ponha-a na variável "
            f"{reescrita.VARIAVEL_DA_CHAVE} ou passe o texto num arquivo")
    print(f"A reescrita usa a API da Anthropic com a sua chave (crie em {reescrita.ONDE_CRIAR_A_CHAVE}).\n"
          "Ela não aparece ao digitar ou colar (no console antigo do Windows, cole com o botão direito),\n"
          "não é gravada e só vai para api.anthropic.com.",
          file=sys.stderr)
    try:
        chave = getpass.getpass("Chave da API (Enter vazio cancela): ")
    except (EOFError, KeyboardInterrupt):
        chave = ""
    if not chave.strip():
        raise reescrita.ErroDeReescrita("cancelada: nenhuma chave digitada")
    return chave


def comando():
    """O comando ``linguagem-simples`` e o ``python -m``: acentos em UTF-8
    também quando a saída vai para arquivo ou pipe (no Windows, o padrão
    seria a página de código local)."""
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    try:
        return main()
    except KeyboardInterrupt:
        return 2
    except Exception as erro:  # defeito do verificador: 2, como erro de uso, nunca o 1
        print(f"{_nome_do_comando()}: erro inesperado ({type(erro).__name__}); avise em "
              f"{ISSUES}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(comando())
